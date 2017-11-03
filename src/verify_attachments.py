import logging
from os.path import split
from drivers import odoo_connector
from drivers.aws_logger import MqttHandler

# Establish MQTT-logger
logger = logging.getLogger('accounting/' + split(__file__)[-1])
logger.setLevel(logging.WARNING)
formatter = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s:%(filename)s:%(message)s")
mqtt_handler = MqttHandler()
mqtt_handler.setFormatter(formatter)
logger.addHandler(mqtt_handler)

#Establish connection
con = odoo_connector.Connection()

#find all attachements in the account.move category
attachment_account_invoice = con.searchRead('ir.attachment', [[['res_model','=','account.invoice'], ['db_datas','<>', None]]], {'fields': ['name', 'res_id', 'id']})
attachment_res_ids = []
for attachment in attachment_account_invoice:
    attachment_res_ids.append(attachment['res_id'])
#Find all supplier invoices not in draft
selection_invoices = con.searchRead('account.invoice', [[['journal_id','=', 2], ['state', '<>', 'draft']]]) #EXJ
selection_invoices += con.searchRead('account.invoice', [[['journal_id','=', 4], ['state', '<>', 'draft']]]) #ECNJ
#Verify that an attachment exists
for move in selection_invoices:
    if move['id'] not in attachment_res_ids:
        logger.warning(move['journal_id'][1] + ' ' + move['internal_number'] + ' dated ' + move['date'] + ' has no attachment!')

#find all attachements in the account.move category
attachment_account_move = con.searchRead('ir.attachment', [[['res_model','=','account.move'], ['db_datas','<>', None]]], {'fields': ['name', 'res_id', 'id']})
attachment_res_ids = []
for attachment in attachment_account_move:
    attachment_res_ids.append(attachment['res_id'])
#Find all journals that needs attachement
selection_moves = con.searchRead('account.move', terms=[[['journal_id','=',5], ['state','=','posted']]]) #DIV
selection_moves += con.searchRead('account.move', terms=[[['journal_id','=',6]]]) #OPEJ
selection_moves += con.searchRead('account.move', terms=[[['journal_id','=',7], ['state','=','posted']]]) #BNK1
selection_moves += con.searchRead('account.move', terms=[[['journal_id','=',8]]]) #BNK2
#Verify that an attachment exists
for move in selection_moves:
    if move['id'] not in attachment_res_ids:
        logger.warning(move['journal_id'][1] + ' ' + move['name'] + ' dated ' + move['date'] + ' has no attachment!')

# Publish all warning to shadow
mqtt_handler.publish_to_shadow(logger.name)