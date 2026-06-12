import json
import os
import sys
from fastapi import APIRouter, Form, HTTPException

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))

if project_root not in sys.path:
    sys.path.append(project_root)

from helpers.context_faq_builder import build_faq_context

router = APIRouter()


@router.post("/api/faq")
async def faq_document(
    project_id: str = Form(...),
    faq_json: str = Form(...)
):
    """
    Receives FAQ input and processes it through FAQ builder.
    """

    if not faq_json:
        raise HTTPException(
            status_code=400,
            detail="You must provide 'faq_json' for the FAQ operation."
        )

    try:
        parsed_faq_json = json.loads(
            faq_json
        )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON format provided in 'faq_json'."
        )

    try:
        print(
            "Starting FAQ context building..."
        )

        processing_result = await build_faq_context(
            project_id=project_id,
            faq_json=parsed_faq_json
        )

        return processing_result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"FAQ Processing Error: {str(e)}"
        )