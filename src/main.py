import requests

from fastapi import FastAPI, HTTPException

from constants import BASE_URL, TEST_API_TOKEN
from models import Track
from orm import create_track, get_statistics, get_user_tracks
from schemas import TrackRequest, TrackResponse

app = FastAPI()


@app.post("/create_a_track/")
def post_track(request: TrackRequest):

    headers = {
        "Accept": "application/json, application/geo+json; charset=utf-8",
        'Authorization': f"Bearer {request.api_token}",
        'Content-Type': 'application/json; charset=utf-8'
    }
    data = {
        "coordinates": [request.start_point, request.finish_point],
        "maximum_speed": request.maximum_speed
    }
    response = requests.post(
        f"{BASE_URL}/v2/directions/{request.profile}",
        json=data, headers=headers
    )

    if response.status_code == 200:
        response_json = response.json()

        new_track = Track(
            api_token=request.api_token,
            name=request.name,
            description=request.description,
            start_point=response_json["metadata"]["query"]["coordinates"][0],
            finish_point=response_json["metadata"]["query"]["coordinates"][1],
            start_datetime=request.start_datetime,
            finish_datetime=request.finish_datetime,
            travel_time=response_json["routes"][0]["summary"]["duration"],
            travel_duration=response_json["routes"][0]["summary"]["distance"]
        )

        create_track(track=new_track)

        return {new_track.id: new_track}

    else:
        raise HTTPException(
            status_code=response.status_code,
            detail="Failed to fetch directions"
        )


@app.get("/user_tracks/{api_token}", response_model=list[TrackResponse])
def get_all_tracks(api_token: str):

    return get_user_tracks(api_token)


@app.get("/calculate_statistics")
async def get_calculate_statistics(
    api_token: str = TEST_API_TOKEN, day_of_week: int = 5
):

    statistics = get_statistics(api_token, day_of_week)

    return statistics

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8889)
