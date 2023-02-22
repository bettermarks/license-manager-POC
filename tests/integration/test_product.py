import pytest


@pytest.mark.asyncio
async def test_get_hero(
        async_client: AsyncClient,
        async_session: AsyncSession,
        test_data: dict
):
    hero_data = test_data["initial_data"]["hero"]
    statement = insert(Hero).values(hero_data)
    await async_session.execute(statement=statement)
    await async_session.commit()

    response = await async_client.get(f"/heroes/{hero_data['uuid']}")
    assert response.status_code == 200

    got = response.json()
    want = test_data["case_get"]["want"]

    for k, v in want.items():
        assert got[k] == v
