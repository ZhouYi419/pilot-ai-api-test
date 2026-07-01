def build_rag_retrieval_payload(project_id, module_id=None, document_id=None):
    payload = {
        "query": "登录失败时系统会怎么处理？",
        "projectId": project_id,
        "topK": 3,
        "minScore": -1.0,
        "maxContextTokens": 3000,
        "includeParentContent": True,
        "currentVersionOnly": True,
    }

    if module_id is not None:
        payload["moduleId"] = module_id

    if document_id is not None:
        payload["documentIds"] = [document_id]

    return payload


def build_invalid_rag_retrieval_payload():
    return {
        "query": "",
        "projectId": None,
    }


def build_rag_question_payload(project_id, module_id=None, document_id=None):
    payload = {
        "question": "登录失败时系统会怎么处理？",
        "projectId": project_id,
        "topK": 3,
        "minScore": -1.0,
        "maxContextTokens": 3000,
        "currentVersionOnly": True,
    }

    if module_id is not None:
        payload["moduleId"] = module_id

    if document_id is not None:
        payload["documentIds"] = [document_id]

    return payload


def build_invalid_rag_question_payload():
    return {
        "question": "",
        "projectId": None,
    }