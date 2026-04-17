from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from maincrew import run_crew
from openai_refiner import openai_refine
from fastapi.responses import StreamingResponse, FileResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from typing import Optional
import os
import random
import time
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
from mcp_integration import serper_search_func

load_dotenv()

app = FastAPI()

fake_db = {}

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RequestData(BaseModel):
    prompt: str
    mode: str

class RefineData(BaseModel):
    output: str
    feedback: str
    mode: str

class EmailRequest(BaseModel):
    email: str
    subject: Optional[str] = None
    content: Optional[str] = None
    report: Optional[str] = None

class VerifyRequest(BaseModel):
    email: str
    otp: str


@app.post("/send-otp")
async def send_otp(req: EmailRequest):
    otp = str(random.randint(100000, 999999))

    fake_db[req.email] = {
        "otp": otp,
        "expires": time.time() + 300  # 5 min expiry
    }

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=req.email,
        subject="OTP Verification",
        plain_text_content=f"Your OTP is {otp}. It expires in 5 minutes."
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)

        print("OTP:", otp)
        print("SendGrid Status:", response.status_code)

        return {"status": "sent"}

    except Exception as e:
        print("ERROR:", str(e))
        raise HTTPException(status_code=500, detail="Failed to send OTP")


@app.post("/verify-otp")
async def verify_otp(req: VerifyRequest):
    user = fake_db.get(req.email)

    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    if time.time() > user["expires"]:
        raise HTTPException(status_code=400, detail="OTP expired")

    if user["otp"] != req.otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    return {"message": "Verified successfully"}


def generate_pdf(text, filename="report.pdf"):
    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()

    story = []

    for line in text.split("\n"):
        if line.strip() == "":
            story.append(Spacer(1, 10))
        else:
            story.append(Paragraph(line, styles["Normal"]))
            story.append(Spacer(1, 8))

    doc.build(story)
    return filename


@app.post("/generate")
def generate(data: RequestData):

    def stream():
        print("Streaming started...") 
        yield "EVENT:SEARCHING\n\n"

        try:
            urls = serper_search_func({
                "query": data.prompt,
                "mode": data.mode
            })
        except Exception as e:
            yield f"EVENT:ERROR:Search failed - {str(e)}\n\n"
            urls = []

        for url in urls[:5]:
            yield f"EVENT:URL:{url}\n\n"

        yield "EVENT:SCRAPING\n\n"

        for url in urls[:5]:
            yield f"EVENT:SCRAPED:{url}\n\n"

        yield "EVENT:RESULT_START\n\n"

        result = run_crew({"query": data.prompt})

        for line in result.split(" "):
            yield line + " "

        yield "\n\nEVENT:RESULT_END\n\n"

    return StreamingResponse(stream(), media_type="text/plain")

@app.post("/refine")
def refine(data: RefineData):
    def stream():
        result = openai_refine(data.output, data.feedback, data.mode)
        for line in result.split(" "):
            yield line + " "
    return StreamingResponse(stream(), media_type="text/plain")

@app.post("/download-pdf")
def download_pdf(data: RefineData):
    formatted = openai_refine(data.output, data.feedback, data.mode)
    file_path = generate_pdf(formatted)

    return FileResponse(
        file_path,
        media_type='application/pdf',
        filename="report.pdf"
    )


@app.post("/send-email")
async def send_email(req: EmailRequest):

    if req.report and req.report.strip():
        subject = "Your AI Generated Report"
        body = f"""

{req.report}

----------------------------------------
"""
    elif req.content and req.content.strip():
        subject = req.subject or "Message from App"
        body = req.content
    else:
        raise HTTPException(
            status_code=400,
            detail="Either 'report' or 'content' must be provided"
        )

    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=req.email,
        subject=subject,
        plain_text_content=body
    )

    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)

        print("Email Status:", response.status_code)

        return {
            "status": "success",
            "message": "Email sent successfully",
            "code": response.status_code
        }

    except Exception as e:
        print("ERROR:", str(e))
        return {
            "status": "failed",
            "error": str(e)
        }