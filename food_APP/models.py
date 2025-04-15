from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

#Make leads
class OutsorceDBLead(models.Model):

    name = models.CharField(max_length=255,null=True, blank=True)
    org_name = models.CharField(max_length=255, null=True, blank=True)
    designation = models.CharField(max_length=225, null=True, blank=True)
    Address = models.TextField(null=True, blank=True)
    contact_number = models.CharField(max_length=15, unique=True)
    mail_id =models.EmailField(null=True, blank=True)
    status = models.CharField(max_length=255)
    source_come_from = models.CharField(max_length=225, default="PDataBase")
    created_at = models.DateTimeField()

class InpersonLead(models.Model):

    B2B = 'B2B'
    B2C = 'B2C'
    LEAD_CATAGORY = [(B2B, 'B2B'),(B2C, 'B2C')]

    BREAKFAST = 'Breakfast'
    LUNCH = 'Lunch'
    DINNER = 'Dinner'
    TEA_SNACKS = 'Tea & Snacks'
    SUPPER = 'Supper'
    ALL = 'All'
    REQUIRED_MEAL_SERVICE = [(BREAKFAST, 'Breakfast'),(LUNCH, 'Lunch'), (DINNER, 'Dinner'), (TEA_SNACKS, 'Tea & Snacks'), (SUPPER, 'Supper'), (ALL, 'All')]

    INDUSTRIAL = 'Industrial'
    CORPORATE = 'Corporate'
    BUSSINESS_EVENT = 'Bussiness_Event'
    OUTHER = ''
    EVENT_TYPE = [(INDUSTRIAL, 'Industrial'),(CORPORATE, 'Corporate'),(BUSSINESS_EVENT,'Bussiness_Event'),(OUTHER,'')]

    IN_HOUSE = 'In_house'
    OUTSOURCE = 'Outsource'
    SERVICE_TYPE = [(IN_HOUSE, 'In_house'),(OUTSOURCE, 'Outsource')]

    NEW = 'NEW'
    PENDING = 'PENDING'
    ATTENDED = 'ATTENDED'
    
    STATUS = [(NEW,'NEW'),(PENDING, 'PENDING'),(ATTENDED,'ATTENDED')]


    lead_generater_name = models.CharField(max_length=225)
    source_come_from = models.CharField(max_length=225, default="Sales_person")
    lead_category = models.CharField(max_length=225, choices=LEAD_CATAGORY)
    name = models.CharField(max_length=225)
    contact_number = models.CharField(max_length=225)
    alternate_number = models.CharField(max_length=225, null=True, blank=True)
    location = models.CharField(max_length=225)
    head_count = models.CharField(max_length=225)
    required_meal_service = models.CharField(max_length=50, choices=REQUIRED_MEAL_SERVICE)
    event_type = models.CharField(max_length=225, choices=EVENT_TYPE)
    company_name = models.CharField(max_length=225)
    designation = models.CharField(max_length=255)
    service_type = models.CharField(max_length=225, choices=SERVICE_TYPE)
    email = models.EmailField()
    event_date_time = models.DateTimeField()
    choice_of_menu = models.TextField(max_length= 200, null=True, blank=True)
    status = models.CharField(max_length=255,choices=STATUS)
    created_at = models.DateTimeField(auto_created=True)


# B2B Lead Model
class B2BLead(models.Model):
    INDUSTRIAL = 'Industrial'
    CORPORATE = 'Corporate'
    TYPE_CHOICES = [(INDUSTRIAL, 'Industrial'), (CORPORATE, 'Corporate')]

    BREAKFAST = 'Breakfast'
    LUNCH = 'Lunch'
    DINNER = 'Dinner'
    TEA_SNACKS = 'Tea & Snacks'
    SUPPER = 'Supper'
    ALL = 'All'
    REQUIRED_MEAL_SERVICE = [(BREAKFAST, 'Breakfast'),(LUNCH, 'Lunch'), (DINNER, 'Dinner'), (TEA_SNACKS, 'Tea & Snacks'), (SUPPER, 'Supper'), (ALL, 'All')]


    VEG = 'Veg'
    NON_VEG = 'Non_Veg'
    VEGAN = 'Vegan'
    DIETARY_OPTIONS =[(VEG, 'Veg'),(NON_VEG, 'Non_Veg'),(VEGAN, 'Vegan')] 

    IN_HOUSE = 'In_house'
    OUTSOURCE = 'Outsource'
    SERVICE_TYPE = [(IN_HOUSE, 'In_house'),(OUTSOURCE, 'Outsource')]

    JUST_DELIVERY = 'Just delivery'
    BUFFET = 'Buffet'
    WITH_SERVICE = 'With Service Person'
    SERVICE_CHOICES = [(JUST_DELIVERY, 'Just delivery'), (BUFFET, 'Buffet'), (WITH_SERVICE, 'With Service Person')]

    MEETING_SCHEDULED = 'Meeting Scheduled'
    MEETING_NOT_SCHEDULED = 'Meeting not Scheduled'
    NOT_INTERESTED  = 'Not Interested'
    STATUS_CHOICES = [
        (MEETING_SCHEDULED, 'Meeting Scheduled'),
        (MEETING_NOT_SCHEDULED, 'Meeting not Scheduled-hold'),
        (NOT_INTERESTED, 'Not Interested')
    ]
    
    name = models.CharField(max_length=255,null=True, blank=True)
    contact_number = models.CharField(max_length=15,unique=True)
    alternate_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    event_type = models.CharField(max_length=50, choices=TYPE_CHOICES,null=True, blank=True)
    company_name = models.CharField(max_length=255,null=True, blank=True)
    designation = models.CharField(max_length=255,null=True, blank=True)
    #event_date_time = models.DateTimeField(null=True, blank=True)
    delivery_location = models.TextField(null=True, blank=True)  # Supports multiple branches
    count = models.IntegerField(default=50,null=True, blank=True)
    required_meal_service = models.CharField(max_length=50, choices=REQUIRED_MEAL_SERVICE,null=True, blank=True)
    dietary_options = models.CharField(max_length=50,choices=DIETARY_OPTIONS, default="Unknown",null=True, blank=True)
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPE, null=True, blank=True)
    service_choice = models.CharField(max_length=50, choices=SERVICE_CHOICES, null=True, blank=True)
    choice_of_menu = models.TextField(max_length= 200, null=True, blank=True)
    existing_menu_budget = models.CharField(max_length=50,null=True, blank=True)
    prefered_menu_budget = models.CharField(max_length=50,null=True, blank=True)
    meeting_date_time = models.DateTimeField(null=True, blank=True)
    lead_status = models.CharField(max_length=225,null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, null=True, blank=True)
    remark = models.TextField(null=True, blank=True)
    lead_score = models.IntegerField(null=True, blank=True)
    from_outsource = models.ForeignKey(OutsorceDBLead, on_delete=models.SET_NULL, null=True, blank=True)
    from_inperson = models.ForeignKey(InpersonLead, on_delete=models.SET_NULL, null=True, blank=True,related_name="b2b_from_inperson")
    lead_generater_name = models.ForeignKey(InpersonLead, on_delete=models.SET_NULL,null=True, blank=True, related_name="b2b_generated_by")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    call_id = models.CharField(max_length=255,unique=True)


    def __str__(self):
        return self.name


# B2C Lead Model
class B2CLead(models.Model):

    BREAKFAST = 'Breakfast'
    LUNCH = 'Lunch'
    DINNER = 'Dinner'
    SNACKS = 'Snacks'
    HI_TEA = 'Hi_tea'
    REQUIRED_MEAL_SERVICE = [(BREAKFAST, 'Breakfast'),(LUNCH, 'Lunch'), (DINNER, 'Dinner'), (SNACKS, 'Snacks'), (HI_TEA, 'Hi_tea')]

    VEG = 'Veg'
    NON_VEG = 'Non_Veg'
    VEGAN = 'Vegan'
    DIETARY_OPTIONS =[(VEG, 'Veg'),(NON_VEG, 'Non_Veg'),(VEGAN, 'Vegan')] 

    JUST_DELIVERY = 'Just delivery'
    BUFFET = 'Buffet'
    WITH_SERVICE = 'With Service Person'
    SERVICE_CHOICES = [(JUST_DELIVERY, 'Just delivery'), (BUFFET, 'Buffet'), (WITH_SERVICE, 'With Service Person')]

    MEETING_SCHEDULED = 'Meeting Scheduled'
    MEETING_NOT_SCHEDULED = 'Meeting not Scheduled'
    STATUS_CHOICES = [
        (MEETING_SCHEDULED, 'Meeting Scheduled'),
        (MEETING_NOT_SCHEDULED, 'Meeting not Scheduled'),
    ]

    customer_name = models.CharField(max_length=255,null=True, blank=True)
    contact_number = models.CharField(max_length=255,unique=True)
    alternate_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    event_type = models.CharField(max_length=255,null=True, blank=True)
    event_date_time = models.DateTimeField(null=True, blank=True)
    delivery_location = models.TextField(null=True, blank=True)
    count = models.IntegerField(null=True, blank=True)
    required_meal_service = models.CharField(max_length=50, choices=REQUIRED_MEAL_SERVICE,null=True, blank=True)
    dietary_options = models.CharField(max_length=50, choices=DIETARY_OPTIONS,default="Unknown",null=True, blank=True)
    service_choice = models.CharField(max_length=50, choices=SERVICE_CHOICES, null=True, blank=True)
    choice_of_menu = models.TextField(max_length= 200, null=True, blank=True)
    existing_menu_budget = models.CharField(max_length=50,null=True, blank=True)
    prefered_menu_budget = models.CharField(max_length=50,null=True, blank=True)
    meeting_date_time = models.DateTimeField(null=True, blank=True)
    lead_status = models.CharField(max_length=225,null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES,null=True, blank=True)
    remark = models.TextField(null=True, blank=True)
    lead_score = models.IntegerField()
    from_outsource = models.ForeignKey(OutsorceDBLead, on_delete=models.SET_NULL, null=True, blank=True)
    from_inperson = models.ForeignKey(InpersonLead, on_delete=models.SET_NULL, null=True, blank=True,related_name="b2c_from_inperson")
    lead_generater_name = models.ForeignKey(InpersonLead, on_delete=models.SET_NULL,null=True, blank=True,related_name="b2c_generated_by")
    created_at = models.DateTimeField(auto_now_add=True)
    call_id = models.CharField(max_length=255, unique=True)


    def __str__(self):
        return self.customer_name

# ---- B2B Follow-Up Bot ----
class B2BFollowUp(models.Model):
    B2B_STATUS_CHOICES = [
        ("meeting_scheduled", "Meeting Scheduled"),
        ("meeting_done", "Meeting Done"),
        ("process_hold", "Process Hold"),
        ("process_further", "Process Further"),
        ("process_finished", "Process Finished"),
        ("kitchen_visit_done", "Kitchen Visit Done"),
        ("sampling_done", "Sampling Done"),
        ("finalized", "Finalized"),
        ("date_confirmed", "Date Confirmed"),
        ("customer", "Converted to Customer"),
    ]

    contact_number = models.CharField(max_length=15)  # Links to B2BLead via phone number
    followup_message = models.TextField()
    followup_status = models.CharField(max_length=50, choices=B2B_STATUS_CHOICES, default="meeting_done")
    feedback = models.TextField(blank=True, null=True)
    followup_date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"B2B Follow-up: {self.contact_number} - {self.followup_status}"


# ---- B2C Follow-Up Bot ----
class B2CFollowUp(models.Model):
    B2C_STATUS_CHOICES = [
        ("meeting_scheduled", "Meeting Scheduled"),
        ("meeting_done", "Meeting Done"),
        ("menu_price_fixed", "Menu and Price Fixed"),
        ("date_confirmed", "Date Confirmed"),
        ("payment_done", "Payment Done"),
        ("customer", "Converted to Customer"),
    ]

    contact_number = models.CharField(max_length=15)  # Links to B2CLead via phone number
    followup_message = models.TextField()
    followup_status = models.CharField(max_length=50, choices=B2C_STATUS_CHOICES, default="meeting_scheduled")
    feedback = models.TextField(blank=True, null=True)
    followup_date_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"B2C Follow-up: {self.contact_number} - {self.followup_status}"


