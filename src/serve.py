from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.cloud import storage
import joblib
import os

app = FastAPI()

ARTIFACT_BUCKET = os.environ.get("ARTIFACT_BUCKET", "track2-d21-2a202601668")
MODEL_KEY = "artifacts/current/model.joblib"
MODEL_PATH = os.path.expanduser("~/models/model.joblib")


def download_model():
    """
    Tai file model.joblib tu cloud storage ve may khi server khoi dong.

    Ham nay duoc goi mot lan khi module duoc import. Su dung
    GOOGLE_APPLICATION_CREDENTIALS de xac thuc (duoc dat trong systemd service).
    """
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    try:
        # TODO 1: Tao storage.Client()
        client = storage.Client()

        # TODO 2: Lay bucket va blob tuong ung
        bucket = client.bucket(ARTIFACT_BUCKET)
        blob = bucket.blob(MODEL_KEY)

        # TODO 3: Tai file model xuong may
        blob.download_to_filename(MODEL_PATH)

        # TODO 4: In thong bao thanh cong
        print("Model da duoc tai xuong tu cloud storage.")
    except Exception as e:
        print(f"Khong the tai model tu Cloud Storage ({e}), su dung model co san tai {MODEL_PATH}")


download_model()
model = joblib.load(MODEL_PATH)


class ScoreRequest(BaseModel):
    features: list[float]


@app.get("/healthz")
def healthz():
    """
    Endpoint kiem tra suc khoe server.
    GitHub Actions goi endpoint nay sau khi deploy de xac nhan server dang chay.

    Tra ve: {"status": "ok"}
    """
    # TODO 5: Tra ve dict {"status": "ok"}
    return {"status": "ok", "model_loaded": model is not None}


@app.post("/score")
def score(req: ScoreRequest):
    """
    Endpoint suy luan chinh.

    Dau vao : JSON {"features": [f1, f2, ..., f10]}
    Dau ra  : JSON {"prediction": <0|1>, "label": <"thu_nhap_thap"|"thu_nhap_cao">}

    Thu tu 10 dac trung (khop voi thu tu trong FEATURE_NAMES cua test):
        age, workclass, education_num, marital_status, occupation,
        relationship, sex, capital_gain, capital_loss, hours_per_week
    """
    # TODO 6: Kiem tra so luong dac trung
    if len(req.features) != 10:
        raise HTTPException(
            status_code=400,
            detail=f"Dau vao can chinh xac 10 dac trung, nhan duoc {len(req.features)}",
        )

    # TODO 7: Goi model.predict([req.features]) de lay ket qua du doan
    prediction = int(model.predict([req.features])[0])

    # TODO 8: Tra ve dict chua "prediction" (int) va "label" (string)
    # Nhan tuong ung: 0 -> "thu_nhap_thap", 1 -> "thu_nhap_cao"
    label = "thu_nhap_cao" if prediction == 1 else "thu_nhap_thap"
    return {"prediction": prediction, "label": label}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)