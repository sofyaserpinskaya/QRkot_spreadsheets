import copy
from datetime import datetime
from http import HTTPStatus
from typing import Dict

from aiogoogle import Aiogoogle
from fastapi import HTTPException

from app.core.config import settings


COLUMN = 11
ROW = 100
TITLE = 'Отчет на {}'

SPREADSHEET_BODY = dict(
    properties=dict(
        locale='ru_RU',
    ),
    sheets=[dict(properties=dict(
        sheetType='GRID',
        sheetId=0,
        title='Лист1',
        gridProperties=dict(
            rowCount=ROW,
            columnCount=COLUMN,
        )
    ))]
)
TABLE_VALUES = [
    ['Отчет от', ''],
    ['Топ проектов по скорости закрытия'],
    ['Название проекта', 'Время сбора', 'Описание']
]

SPREADSHEET_SIZE_ERROR = (
    'Количество передаваемых данных не помещается в таблице. '
    'Вы передаете {my_row} строк {my_column} столбцов. '
    'Размер таблицы: {row} строк {column} столбцов.'
)


async def spreadsheets_create(
    wrapper_services: Aiogoogle,
    now_date_time: datetime,
    spreadsheet_body: Dict = copy.deepcopy(SPREADSHEET_BODY),
) -> str:
    spreadsheet_body['properties']['title'] = TITLE.format(str(now_date_time))
    service = await wrapper_services.discover('sheets', 'v4')
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    return response['spreadsheetId']


async def set_user_permissions(
        spreadsheet_id: str,
        wrapper_services: Aiogoogle
) -> None:
    permissions_body = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': settings.email
    }
    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheet_id,
            json=permissions_body,
            fields="id"
        ))


async def spreadsheets_update_value(
        spreadsheet_id: str,
        projects: list,
        wrapper_services: Aiogoogle,
        now_date_time: datetime,
) -> None:
    service = await wrapper_services.discover('sheets', 'v4')
    projects_fields = sorted((
        (
            project.name,
            project.close_date - project.create_date,
            project.description
        ) for project in projects
    ), key=lambda x: x[1])
    header = copy.deepcopy(TABLE_VALUES)
    header[0][1] = str(now_date_time)
    table_values = [
        *header,
        *[list(map(str, field)) for field in projects_fields],
    ]
    my_row, my_column = len(table_values), max(len(table) for table in header)
    if my_row > ROW and my_column > COLUMN:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=SPREADSHEET_SIZE_ERROR.format(
                my_row=my_row, my_column=my_column,
                row=ROW, column=COLUMN
            ),
        )
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range=f'R1C1:R{ROW}C{COLUMN}',
            valueInputOption='USER_ENTERED',
            json={
                'majorDimension': 'ROWS',
                'values': table_values
            }
        )
    )
