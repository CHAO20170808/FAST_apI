import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fastapi.testclient import TestClient
import main1
from fastapi import status

#from fastapi.testclient import TestClient
#from . import main1  # 使用相對導入
#from fastapi import status


client = TestClient(main1.app)


def test_return_health_check():
    response = client.get("/healthy")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'status':'Healthy'}
