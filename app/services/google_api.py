from datetime import datetime
from typing import Dict

from aiogoogle import Aiogoogle

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


async def spreadsheets_create(
    wrapper_services: Aiogoogle,
    now_date_time: datetime,
    spreadsheet_body: Dict = SPREADSHEET_BODY,
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
    projects_filelds = sorted((
        (
            project.name,
            project.close_date - project.create_date,
            project.description
        ) for project in projects
    ), key=lambda x: x[1])
    TABLE_VALUES[0][1] = str(now_date_time)
    table_values = [
        *TABLE_VALUES,
        *[list(map(str, field)) for field in projects_filelds],
    ]
    if (
        len(table_values) <= ROW and
        max(len(table) for table in TABLE_VALUES) <= COLUMN
    ):
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
