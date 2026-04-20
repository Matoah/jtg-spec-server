from configs import spec_server_config
from requests import post, get

KNOWLEDGE_DATASET_NAME_ID = {

}


def _post_json(uri: str, **kwargs):
    """post请求"""
    headers = {
        "Authorization": f"Bearer {spec_server_config.KNOWLEDGE_API_KEY}",
        "Content-Type": "application/json",
    }
    response = post(f"{spec_server_config.KNOWLEDGE_BASE_URI}/{uri}", headers=headers, **kwargs)
    response.raise_for_status()
    return response


def _get(uri: str, **kwargs):
    """get请求"""
    headers = {
        "Authorization": f"Bearer {spec_server_config.KNOWLEDGE_API_KEY}",
    }
    response = get(f"{spec_server_config.KNOWLEDGE_BASE_URI}/{uri}", headers=headers, **kwargs)
    response.raise_for_status()
    return response


def get_dataset_id():
    """
    获取知识库数据集ID
    :return:
    """
    dataset_name = spec_server_config.KNOWLEDGE_DATASET
    if dataset_name in KNOWLEDGE_DATASET_NAME_ID:
        return KNOWLEDGE_DATASET_NAME_ID[dataset_name]
    has_more = True
    page = 1
    while has_more:
        response = _get(
            "datasets",
            params={"keyword": dataset_name, "include_all": True, "page": page}
        )
        response_json = response.json()
        has_more = response_json.get("has_more", False)
        page += 1
        data = response_json.get("data", [])
        for dataset in data:
            if dataset["name"] == dataset_name:
                return dataset["id"]
    raise ValueError(f"知识库【{dataset_name}】不存在")


def retrieve_document(query: str, top_k: int = 10) -> list[dict]:
    """
    检索知识库
    :param query: 检索查询
    :param top_k: 返回结果数量
    :return: 检索结果
    """
    dataset_id = get_dataset_id()
    response = _post_json(
        f"datasets/{dataset_id}/retrieve",
        json={
            "query": query,
            "retrieval_model": {
                "search_method": "hybrid_search",
                "reranking_enable": True,
                "weights": None,
                "top_k": top_k,
                "score_threshold_enabled": False,
                "score_threshold": None
            }
        }
    )
    response_json = response.json()
    return response_json.get("records", [])
