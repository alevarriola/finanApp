import strawberry
from aioinject import Injected
from aioinject.ext.strawberry import inject

from app.graphql.reports.services.report_service import ReportService
from app.graphql.reports.types.report_types import DashboardFiltersInput, DashboardSummary


@strawberry.type
class ReportQueries:
    @strawberry.field
    @inject
    async def dashboard_summary(
        self,
        filters: DashboardFiltersInput,
        service: Injected[ReportService],
    ) -> DashboardSummary:
        return await service.get_dashboard_summary(filters)

    @strawberry.field
    @inject
    async def available_currencies(
        self,
        service: Injected[ReportService],
    ) -> list[str]:
        return await service.get_available_currencies()
