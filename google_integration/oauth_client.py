"""Google Drive/Sheets integration. OAuth runs in the desktop Tkinter process."""
from __future__ import annotations
import os
from pathlib import Path
from typing import Sequence
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# The app creates the spreadsheets it exports, so per-file Drive access is enough.
SCOPES = ["https://www.googleapis.com/auth/drive.file"]
ROOT = Path(__file__).resolve().parents[1]


def user_credentials():
    client_file = Path(os.getenv("GOOGLE_OAUTH_CLIENT_FILE", ROOT / "config" / "oauth_client.json"))
    token_file = Path(os.getenv("GOOGLE_OAUTH_TOKEN_FILE", ROOT / "config" / "token.json"))
    credentials = None
    if token_file.exists():
        credentials = Credentials.from_authorized_user_file(str(token_file), SCOPES)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            if not client_file.exists():
                raise FileNotFoundError(f"OAuth JSON не найден: {client_file}")
            flow = InstalledAppFlow.from_client_secrets_file(str(client_file), SCOPES)
            credentials = flow.run_local_server(port=0)
        token_file.parent.mkdir(parents=True, exist_ok=True)
        token_file.write_text(credentials.to_json(), encoding="utf-8")
    return credentials


class GoogleExport:
    def __init__(self):
        creds = user_credentials()
        self.drive = build("drive", "v3", credentials=creds, cache_discovery=False)
        self.sheets = build("sheets", "v4", credentials=creds, cache_discovery=False)

    def create_report(self, title: str, headers: Sequence[str], rows: Sequence[Sequence[object]]) -> str:
        folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "").strip()
        body = {"name": title, "mimeType": "application/vnd.google-apps.spreadsheet"}
        if folder_id:
            body["parents"] = [folder_id]
        file = self.drive.files().create(body=body, fields="id,name,webViewLink").execute()
        spreadsheet_id = file["id"]
        values = [list(headers), *[list(row) for row in rows]]
        self.sheets.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range="A1", valueInputOption="RAW", body={"values": values}
        ).execute()
        self.sheets.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body={"requests": [
            {"repeatCell": {"range": {"sheetId": 0, "startRowIndex": 0, "endRowIndex": 1},
                            "cell": {"userEnteredFormat": {"backgroundColor": {"red": .30, "green": .24, "blue": .75},
                                                             "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}}}},
                            "fields": "userEnteredFormat(backgroundColor,textFormat)"}},
            {"autoResizeDimensions": {"dimensions": {"sheetId": 0, "dimension": "COLUMNS", "startIndex": 0, "endIndex": len(headers)}}}
        ]}).execute()
        return file.get("webViewLink", f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit")
