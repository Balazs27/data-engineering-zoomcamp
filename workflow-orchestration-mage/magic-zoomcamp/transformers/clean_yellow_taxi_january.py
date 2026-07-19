if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def clean_yellow_taxi_january(data, *args, **kwargs):
    """Remove invalid passenger counts and rows outside January 2021."""
    pickup = data['tpep_pickup_datetime']
    passenger_count = data['passenger_count']
    keep = (
        passenger_count.notna()
        & passenger_count.gt(0)
        & pickup.ge('2021-01-01')
        & pickup.lt('2021-02-01')
    )
    return data.loc[keep].copy()


@test
def test_output(output, *args) -> None:
    assert output is not None, 'The output is undefined'
    assert not output.empty, 'The transformed dataset is empty'
    assert output['passenger_count'].gt(0).all()
    assert output['tpep_pickup_datetime'].ge('2021-01-01').all()
    assert output['tpep_pickup_datetime'].lt('2021-02-01').all()
