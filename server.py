
from typing import Type
from flask import Flask, jsonify, request
from flask.views import MethodView
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from models import Session, Ad
from schema import CreateAd, PatchAd

app = Flask('app')


def validate_ad(json_data: dict, model_class):
    try:
        model_item = model_class(**json_data)
        return model_item.dict(exclude_none=True)
    except ValidationError as err:
        raise HttpError(400, err.errors())


class HttpError(Exception):
    def __init__(self, status_code: int, message) -> None:
        self.status_code = status_code
        self.message = message
        

@app.errorhandler(HttpError)
def error_handler(error: HttpError):
    response = jsonify({'status': 'error', 'message': error.message})
    response.status_code = error.status_code
    return response


def get_ad(ad_id: int, session: Session) -> Ad:
    ad = session.get(Ad, ad_id)
    if ad is None:
        raise HttpError(404, message='Ad not found')
    return ad

class AdView(MethodView):
    
    def get(self, ad_id: int):
        with Session() as session:
            ad = get_ad(ad_id, session)
            return jsonify({
                'id': ad.id,
                'title': ad.title,
                'description': ad.description,
                'creation_time': ad.creation_time.isoformat(),
                'owner': ad.owner,
            })

    def delete(self, ad_id: int):
        with Session() as session:
            ad = get_ad(ad_id, session)
            session.delete(ad)
            session.commit()
            return jsonify({
                'status': 'success'
            })

    def patch(self, ad_id: int):
        json_data = validate_ad(request.json, PatchAd)
        with Session() as session:
            ad = get_ad(ad_id, session)
            for field, value in json_data.items():
                setattr(ad, field, value)    
            try:
                session.commit()
            except IntegrityError as err:
                raise HttpError(409, 'title is busy')
            return jsonify({
                'id': ad.id
            })

    def post(self):
        json_data = validate_ad(request.json, CreateAd)
        with Session() as session:
            new_ad = Ad(**json_data)
            session.add(new_ad)
            try:
                session.commit()
            except IntegrityError as err:
                raise HttpError(409, 'ad already exists')    
            return jsonify({
                'id': new_ad.id
            })
    

app.add_url_rule('/ads/', view_func=AdView.as_view('ad_new'), methods=['POST', ])
app.add_url_rule('/ads/<int:ad_id>/', view_func=AdView.as_view('ad_existed'), methods=['GET', 'DELETE', 'PATCH', ])

if __name__ == "__main__":
    app.run()