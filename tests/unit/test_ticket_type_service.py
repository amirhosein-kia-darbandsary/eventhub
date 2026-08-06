import pytest

from app.services.ticket_type_service import calculate_available


@pytest.mark.unit
def test_available_with_no_reservations_or_sales():
    assert calculate_available(total_quantity=100, reserved_quantity=0, sold_quantity=0) == 100


@pytest.mark.unit
def test_available_subtracts_reserved_and_sold():
    assert calculate_available(total_quantity=100, reserved_quantity=10, sold_quantity=20) == 70


@pytest.mark.unit
def test_available_can_be_zero_when_fully_sold_out():
    assert calculate_available(total_quantity=50, reserved_quantity=0, sold_quantity=50) == 0


@pytest.mark.unit
def test_available_can_go_negative_if_data_is_inconsistent():
    # Vars Validations are in the other layer here just testing calculation service
    assert calculate_available(total_quantity=10, reserved_quantity=8, sold_quantity=5) == -3