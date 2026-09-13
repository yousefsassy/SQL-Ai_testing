def calculate_local_cost_per_1000(
    hardware_cost_per_hour,
    requests_per_hour,
    human_cost_per_1000=0.0
):
    if requests_per_hour <= 0:
        raise ValueError(
            "requests_per_hour must be greater than zero"
        )

    hardware_cost_per_request = (
        hardware_cost_per_hour /
        requests_per_hour
    )

    hardware_cost_per_1000 = (
        hardware_cost_per_request * 1000
    )

    total_cost_per_1000 = (
        hardware_cost_per_1000 +
        human_cost_per_1000
    )

    return {
        "hardware_cost_per_1000":
            hardware_cost_per_1000,

        "human_cost_per_1000":
            human_cost_per_1000,

        "total_cost_per_1000":
            total_cost_per_1000
    }