def resolve_mode_from_csv(entry, merchant_name, current_mode, merchant_mode_map):
    """
    Returns updated mode based on CSV mapping.
    Prints full transaction when updated or not found.
    """
    for csv_merchant, csv_mode in merchant_mode_map.items():
        if csv_merchant.lower() in merchant_name.lower():
            if current_mode != csv_mode:
                print(f"UPDATED: {entry}  ==>  {csv_mode}")
            return csv_mode

    print(f"NOT FOUND: {entry}")
    return current_mode
