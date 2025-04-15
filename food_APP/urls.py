from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    generate_twiml, call_ai_agent, vapi_webhook, process_vapi_responses, stop_call,
    get_outsource_leads, get_inperson_leads, get_b2b_leads, get_b2c_leads,
    export_b2b_excel, export_b2c_excel,upload_excel,
    fetch_bot_leads, followup_bot, 
    b2b_list, b2b_create, b2b_detail, b2b_update, b2b_delete,
    b2c_list, b2c_create, b2c_detail, b2c_update, b2c_delete,
)

urlpatterns = [

    path('twiml/<int:lead_id>/', generate_twiml, name='generate_twiml'),
    path('webhook/', vapi_webhook, name='vapi_webhook'),

    # Outbound Call APIs
    path('call-ai-agent/', call_ai_agent, name='call_ai_agent'),
    path('stop-call/', stop_call, name='stop_call'), 
    path('process-vapi-responses/', process_vapi_responses, name='process_vapi_responses'),

    path("outsource/", get_outsource_leads),
    path("inperson/", get_inperson_leads),
    path("get_b2b/", get_b2b_leads),
    path("get_b2c/", get_b2c_leads),

    path("upload_excel/",upload_excel),

    path("export_b2b/", export_b2b_excel),
    path("export_b2c/", export_b2c_excel),

    # Fetch Leads
    path('fetch-bot-leads/', fetch_bot_leads, name='fetch-bot-leads'),

    # WhatsApp Follow-Up Bot
    path('followup-bot/', followup_bot, name='followup_bot'),

    # B2B Lead CRUD
    path('b2b/', b2b_list, name='b2b-list'),
    path('b2b/create/', b2b_create, name='b2b-create'),
    path('b2b/<int:pk>/', b2b_detail, name='b2b-detail'),
    path('b2b/update/<int:pk>/', b2b_update, name='b2b-update'),
    path('b2b/delete/<int:pk>/', b2b_delete, name='b2b-delete'),

    # B2C Lead CRUD
    path('b2c/', b2c_list, name='b2c-list'),
    path('b2c/create/', b2c_create, name='b2c-create'),
    path('b2c/<int:pk>/', b2c_detail, name='b2c-detail'),
    path('b2c/update/<int:pk>/', b2c_update, name='b2c-update'),
    path('b2c/delete/<int:pk>/', b2c_delete, name='b2c-delete'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)