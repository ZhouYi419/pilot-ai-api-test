def build_functional_test_case_generation_payload(project_id, module_id=None, document_id=None):
    payload = {
        "projectId": project_id,
        "generationGoal": "围绕登录模块生成覆盖正常流程、异常流程和边界场景的功能测试用例",
        "caseCount": 3,
        "topK": 3,
        "minScore": -1.0,
        "maxContextTokens": 4000,
        "currentVersionOnly": True,
    }

    if module_id is not None:
        payload["moduleId"] = module_id

    if document_id is not None:
        payload["documentIds"] = [document_id]

    return payload


def build_invalid_functional_test_case_generation_payload():
    return {
        "projectId": None,
        "generationGoal": "",
    }