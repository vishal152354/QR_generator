import qrcode
from PIL import Image
from fastapi import FastAPI , Request , HTTPException 
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from fastapi.templating import Jinja2Templates


class Item(BaseModel):
    laptopModel: str
    employeeId: str
    
app = FastAPI()
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

@app.get("/")
def read_root(request:Request):
    return templates.TemplateResponse("index.html",{"request": request})

@app.post("/submit-data")
async def handle_data(item: Item):
    qr_data = f"Laptop Model: {item.laptopModel}, Employee ID: {item.employeeId}"
    
 
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    
    img = qr.make_image(fill_color="black", back_color="white")


    filename = f"qrcode_{item.employeeId}.png"
    img_path = Path("./qrcodes") / filename
    

    img_path.parent.mkdir(parents=True, exist_ok=True)
    

    img.save(img_path)

    return {
        "status": "success", 
        "message": "Data received and QR code generated successfully!",
        "file_path": str(img_path),
        "download_url": f"/download-qr/{filename}"
    }
@app.get("/download-qr/{filename}")
async def download_qr(filename: str):
    """
    Allows a user to download a previously generated QR code image.
    """
    file_path = Path("./qrcodes") / filename
    
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
        
    return FileResponse(
        path=file_path,
        media_type="image/jpeg",
        filename=filename
    )