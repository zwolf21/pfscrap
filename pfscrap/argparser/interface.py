def set_argparser(argparser):
    argparser.add_argument(
        'keywords',
        help='스크랩분야 지정(ls-펀드리스트, ls-al-펀드리스트자세히, cat-펀드정보, pg-가격변동추이, ex-결산및상환)',
        nargs='+'
    )
    argparser.add_argument(
        '-fcd', '--fund_std_code',
        help='펀드표준코드',
        # nargs='?',
    )
    argparser.add_argument(
        '-ini', '--initial_date',
        help='연관정보 조회 시작일',
        nargs='*',
        type=str,
    )
    argparser.add_argument(
        '-sd', '--start_date',
        help='펀드설정일 시작일자',
        type=str
    )
    argparser.add_argument(
        '-ed', '--end_date',
        help='펀드설정일 종료일자',
        type=str
    )
    argparser.add_argument(
        '-da', '--day_ago',
        help='펀드설정일 시작일자: 현재로 부터 이전 일수',
        type=int,
    )
    argparser.add_argument(
        '-ma', '--month_ago',
        help='펀드설정일 시작일자: 현재로 부터 이전 월수',
        type=int,
    )
    argparser.add_argument(
        '-ya', '--year_ago',
        help='펀드설정일 시작일자: 현재로 부터 이전 년수',
        type=int,
    )
    argparser.add_argument(
        '-o', '--output',
        help='결과물 출력파일 형식지정("csv", "xlsx", Path of the DB Connection info file)',
        nargs='?',
        type=str,
    )
    argparser.add_argument(
        '-conn', '--db_conf_path',
        help='MySQL DB connection 정보 들어있는 파일지정',
        type=str
    )
