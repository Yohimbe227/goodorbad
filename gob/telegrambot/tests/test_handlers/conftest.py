import pytest
import requests_mock


@pytest.fixture
def mock_geocode_maps(monkeypatch):
    def _mock_get(*args, **kwargs):
        return {
            "response": {
                "GeoObjectCollection": {
                    "featureMember": [
                        {"GeoObject": {"Point": {"pos": "37.617698 55.755864"}}}
                    ]
                }
            }
        }

    monkeypatch.setattr(requests_mock.Mocker, "get", _mock_get)
    return requests_mock.Mocker()


@pytest.fixture
async def state_data(*args, **kwargs):
    return {
        "category": "бар",
    }

