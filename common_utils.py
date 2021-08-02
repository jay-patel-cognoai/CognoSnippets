from EasyChatApp.models import *
import json
from EasyChatApp.utils import logger

try:
    
    #===========================================================
    # intent_tree_pk is the tree pk of the processor or api tree
    #===========================================================
    
    #===========================================================
    # call function as => result_dict['enable_datepicker'](1367)
    #===========================================================
    def enable_datepicker(intent_tree_pk):
        res_obj = Tree.objects.get(pk=intent_tree_pk).response
        temp_rec = json.loads(res_obj.modes)
        temp_rec['is_datepicker'] = 'true'
        temp_rec['is_single_datepicker'] ='true'
        res_obj.modes = json.dumps(temp_rec)
        res_obj.save()
        
    #===========================================================
    # call function as => result_dict['disable_datepicker'](1367)    
    #===========================================================
    def disable_datepicker(intent_tree_pk):
        res_obj = Tree.objects.get(pk=intent_tree_pk).response
        temp_rec = json.loads(res_obj.modes)
        temp_rec['is_datepicker'] = 'false'
        temp_rec['is_single_datepicker'] ='false'
        res_obj.modes = json.dumps(temp_rec)
        res_obj.save()
        
    #===========================================================
    # call function as => result_dict['enable_otp_timer'](1367) 
    #===========================================================
    def enable_otp_timer(intent_tree_pk):
        res_obj = Tree.objects.get(pk=intent_tree_pk).response
        temp_rec = json.loads(res_obj.modes)
        temp_rec["show_otp_timmer"] = "true"
        res_obj.modes = json.dumps(temp_rec)
        res_obj.save()
    
    #===========================================================
    # call function as => result_dict['disable_otp_timer'](1367)
    #===========================================================
    def disable_otp_timer(intent_tree_pk):
        res_obj = Tree.objects.get(pk=intent_tree_pk).response
        temp_rec = json.loads(res_obj.modes)
        temp_rec["show_otp_timmer"] = "false"
        res_obj.modes = json.dumps(temp_rec)
        res_obj.save()
    
    #===========================================================
    # call function as => result_dict['enable_recommendation_menu'](1367)
    #===========================================================
    def enable_recommendation_menu(intent_tree_pk):
        res_obj = Tree.objects.get(pk=intent_tree_pk).response
        temp_rec = json.loads(res_obj.modes)
        temp_rec["is_recommendation_menu"] = "true"
        res_obj.modes = json.dumps(temp_rec)
        res_obj.save()
    
    #===========================================================
    # call function as => result_dict['disable_recommendation_menu'](1367)
    #===========================================================
    def disable_recommendation_menu(intent_tree_pk):
        res_obj = Tree.objects.get(pk=intent_tree_pk).response
        temp_rec = json.loads(res_obj.modes)
        temp_rec["is_recommendation_menu"] = "false"
        res_obj.modes = json.dumps(temp_rec)
        res_obj.save()
    
    #===========================================================
    # call function as => result_dict['get_sortedlist_dropdown'](1367,['a','b','c'])
    #===========================================================
    def get_sortedlist_dropdown(intent_tree_pk,intent_list_dp):
        res_obj = Tree.objects.get(pk=intent_tree_pk).response
        temp_rec = json.loads(res_obj.modes_param)
        temp_rec['drop_down_choices'] = sorted(intent_list_dp)
        res_obj.modes_param = json.dumps(temp_rec)
        res_obj.save()
    
    #===========================================================
    # call function as => result_dict['get_unsortedlist_dropdown'](1367,['a','b','c'])
    #===========================================================
    def get_unsortedlist_dropdown(intent_tree_pk,intent_list_dp):
        res_obj = Tree.objects.get(pk=intent_tree_pk).response
        temp_rec = json.loads(res_obj.modes_param)
        temp_rec['drop_down_choices'] = intent_list_dp
        res_obj.modes_param = json.dumps(temp_rec)
        res_obj.save()
    
except Exception as E:
    exc_type, exc_obj, exc_tb = sys.exc_info()
    logger.error('Common_utils_1: %s at %s',str(E), str(exc_tb.tb_lineno), extra={'AppName': 'EasyChat', 'user_id': 'None', 'source': 'None', 'channel': 'None', 'bot_id': 'None'})
    
    

    
