def test_get_moves(client):
    response = client.get("/moves/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_move_not_found(client):
    response = client.get("/moves/999999")
    assert response.status_code == 404
