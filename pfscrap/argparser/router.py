from .kofia.parser import parse_kofia_args


def route(args):
    keywords = args.keywords
    if isinstance(keywords, str):
        keywords = [keywords]
    if len(keywords) != 2:
        error_message = "It requires 2 keywords (>> pfscrap scrap_appname action)"
        raise ValueError(error_message)

    app_name, action = keywords

    if app_name == 'kofia':
        parse_kofia_args(
            action,
            start_date=args.start_date,
            end_date=args.end_date,
            output=args.output
        )
