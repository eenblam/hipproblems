def get_agony(flight_record):
    try:
        return flight_record['agony']
    except KeyError as e:
        raise KeyError('Could not extract agony from flight record')
