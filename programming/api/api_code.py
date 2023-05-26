from get_opinion_pairs import get_pairs_dict, parse_text
from models_analysis import load_tokenizer_from_file, load_model_from_file, analyse_review
import os
import uvicorn
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


class Review(BaseModel):
    text: str


class API_Controller():
    def __init__(self, model, tokenizer) -> None:
        self.model = model
        self.tokenizer = tokenizer
        self.router = APIRouter()
        self.router.add_api_route(
            "/sentiment", self.sentiment, methods=["POST"])
        self.router.add_api_route("/aspect", self.aspect, methods=["POST"])

    async def sentiment(self, obj: Review):
        review = obj.text
        result = analyse_review(self.model, self.tokenizer, review)
        return {"result": float(result[0][0])}

    async def aspect(self, obj: Review):
        review = obj.text
        ann = parse_text(review)
        result = get_pairs_dict(ann)
        return {"result": result}


if __name__ == "__main__":
    os.environ["CORENLP_HOME"] = "../stanford-corenlp-4.5.4"

    model_path = "../models/c1_cnn_model_acc_0.881.h5"
    tokenizer_path = "../preparing/b3_tokenizer.json"

    model = load_model_from_file(model_path)
    tokenizer = load_tokenizer_from_file(tokenizer_path)

    app = FastAPI()
    cntrllr = API_Controller(model, tokenizer)
    app.include_router(cntrllr.router)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    uvicorn.run(app, host="127.0.0.1", port=5000)
