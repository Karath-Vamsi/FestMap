import os
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import json

load_dotenv()

FIRESTORE_COLLECTION = os.getenv("FIRESTORE_COLLECTION", "festivals")
firebase_creds_str = os.getenv("FIREBASE_CREDENTIALS_JSON")
firebase_creds = json.loads(firebase_creds_str) if firebase_creds_str else None

def init_firestore():
    if not firebase_creds:
        raise Exception("Firebase credentials JSON is not set in environment variables.")

    cred = credentials.Certificate(firebase_creds)

    try:
        firebase_admin.get_app()
    except ValueError:
        firebase_admin.initialize_app(cred)
    return firestore.client()


def save_festival_data(festival_list):
    """
    Saves each story and ritual to the appropriate festival document using Firestore ArrayUnion.
    Structure:
    festivals/
        dasara/
            stories: [story1, story2, ...]
            rituals: [ritual1, ritual2, ...]
    """
    db = init_firestore()
    for fest in festival_list:
        name = fest.get("festival_name", "other").strip().lower()
        story = fest.get("story", "").strip()
        rituals = fest.get("rituals", "").strip()

        if not story and not rituals:
            continue

        update_data = {}
        if story:
            update_data["stories"] = firestore.ArrayUnion([story])
        if rituals:
            update_data["rituals"] = firestore.ArrayUnion([rituals])

        if update_data:
            doc_ref = db.collection(FIRESTORE_COLLECTION).document(name)
            doc_ref.set(update_data, merge=True)
            print(f"Appended to festival '{name}'")