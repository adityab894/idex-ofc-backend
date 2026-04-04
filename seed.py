import json
from app.database import SessionLocal, Base, engine
from app.models import OFCSegment, SegmentStatus


Base.metadata.create_all(bind=engine, checkfirst=True)

def seed_db():
    db = SessionLocal()
    if db.query(OFCSegment).first():
        print("Database already seeded with segments!")
        db.close()
        return

    print("Seeding Indian Air Force Mock Nodes and Connections...")


    mock_segments = [
        {
            "name": "Hindon - Ambala OFC Link",
            "base_code": "AF-01",
            "length_km": 200.5,
            "route_geojson": {
                "type": "LineString",
                "coordinates": [
                    [77.3556, 28.7051], # Hindon area approx
                    [76.7820, 30.3546]  # Ambala approx
                ]
            }
        },
        {
            "name": "Ambala - Chandigarh Backbone",
            "base_code": "AF-02",
            "length_km": 45.2,
            "route_geojson": {
                "type": "LineString",
                "coordinates": [
                    [76.7820, 30.3546], # Ambala
                    [76.7821, 30.6728]  # Chandigarh
                ]
            }
        },
        {
            "name": "Chandigarh - Adampur Trunk",
            "base_code": "AF-03",
            "length_km": 150.0,
            "route_geojson": {
                "type": "LineString",
                "coordinates": [
                    [76.7821, 30.6728], # Chandigarh
                    [75.7608, 31.4338]  # Adampur
                ]
            }
        },
        {
            "name": "Adampur - Pathankot Forward Link",
            "base_code": "AF-04",
            "length_km": 105.8,
            "route_geojson": {
                "type": "LineString",
                "coordinates": [
                    [75.7608, 31.4338], # Adampur
                    [75.6418, 32.2289]  # Pathankot
                ]
            }
        }
    ]

    for data in mock_segments:
        segment = OFCSegment(
            name=data["name"],
            base_code=data["base_code"],
            length_km=data["length_km"],
            route_geojson=data["route_geojson"],
            status=SegmentStatus.healthy,
            availability_30d_pct=99.98
        )
        db.add(segment)
        print(f"Added Segment: {data['name']}")

    db.commit()
    db.close()
    print("Seeding Complete!")

if __name__ == "__main__":
    seed_db()
