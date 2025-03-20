from fastapi import FastAPI
from app.routers import addUser, buyPackage, cancelOrder, checkUser, depositTransaction, placeOrder, showOrder, showPackage, showTransaction, updateAddress, userDetails, verifyOtp, encryption, decryption
from app.getDetails import advertisement, allServices, appDetails, availableDates, displayPackages, fetchCoupons, preferences
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# Include routers
app.include_router(addUser.router, prefix="/api", tags=["addUser"])
app.include_router(buyPackage.router, prefix="/api", tags=["buyPackage"])
app.include_router(cancelOrder.router, prefix="/api", tags=["cancelOrder"])
app.include_router(checkUser.router, prefix="/api", tags=["checkUser"])
app.include_router(depositTransaction.router, prefix="/api", tags=["depositTransaction"])
app.include_router(placeOrder.router, prefix="/api", tags=["placeOrder"])
app.include_router(showOrder.router, prefix="/api", tags=["showOrder"])
app.include_router(showPackage.router, prefix="/api", tags=["showPackage"])
app.include_router(showTransaction.router, prefix="/api", tags=["showTransaction"])
app.include_router(updateAddress.router, prefix="/api", tags=["updateAddress"])
app.include_router(userDetails.router, prefix="/api", tags=["userDetails"])
app.include_router(verifyOtp.router, prefix="/api", tags=["verifyOtp"])
app.include_router(encryption.router, prefix="/api", tags=["encrypt"])
app.include_router(decryption.router, prefix="/api", tags=["decrypt"])

app.include_router(advertisement.router, prefix="/api", tags=["advertisement"])
app.include_router(allServices.router, prefix="/api", tags=["allServices"])
app.include_router(appDetails.router, prefix="/api", tags=["appDetails"])
app.include_router(availableDates.router, prefix="/api", tags=["availableDates"])
app.include_router(displayPackages.router, prefix="/api", tags=["displayPackages"])
app.include_router(fetchCoupons.router, prefix="/api", tags=["fetchCoupons"])
app.include_router(preferences.router, prefix="/api", tags=["preferences"])

@app.get("/")
async def root():
    return {"message": "Welcome to the combined FastAPI app"}
