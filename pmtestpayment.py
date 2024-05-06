#!/usr/bin/python3

import payment
import billmgr.db
import billmgr.exception

import billmgr.logger as logging

import xml.etree.ElementTree as ET
import tinkoffapi
from tinkoffapi import PaymentStatus

MODULE = 'payment'
logging.init_logging('pmtestpayment')
logger = logging.get_logger('pmtestpayment')

class TestPaymentModule(payment.PaymentModule):
    def __init__(self):
        super().__init__()

        self.features[payment.FEATURE_CHECKPAY] = True
        self.features[payment.FEATURE_REDIRECT] = True
        self.features[payment.FEATURE_NOT_PROFILE] = True
        self.features[payment.FEATURE_PMVALIDATE] = True

        self.params[payment.PAYMENT_PARAM_PAYMENT_SCRIPT] = "/mancgi/testpayment"

    def PM_Validate(self, xml : ET.ElementTree):
        logger.info("run pmvalidate")

        # мы всегда можем вывести xml в лог, чтобы изучить, что приходит :)
        logger.info(f"xml input: {ET.tostring(xml.getroot(), encoding='unicode')}")

        terminalkey_node = xml.find('./terminalkey')
        terminalpsw_node = xml.find('./terminalpsw')
        minamount_node = xml.find('./paymethod/minamount')

        terminalkey = terminalkey_node.text if terminalkey_node is not None else ''
        terminalpsw = terminalpsw_node.text if terminalpsw_node is not None else ''
        minamount = float(minamount_node.text) if minamount_node is not None else 0.0

        if minamount < 1.0:
            raise billmgr.exception.XmlException("msg_error_too_small_min_amount")

        # TODO: проверка валидности терминала

    # в тестовом примере получаем необходимые платежи
    # и переводим их все в статус 'оплачен'
    def CheckPay(self):
        logger.info("run checkpay")

        # получаем список платежей в статусе оплачивается
        # и которые используют обработчик pmtestpayment
        payments = billmgr.db.db_query(f'''
            SELECT p.id, p.externalid, p.info, pm.xmlparams FROM payment p
            JOIN paymethod pm
            WHERE module = 'pmtestpayment' AND p.status = {payment.PaymentStatus.INPAY.value}
        ''')

        for p in payments:
            try:
                logger.info(f"change status for payment {p['id']}")

                xmlparams = ET.ElementTree(ET.fromstring(p['xmlparams']))
                terminalkey_node = xmlparams.find('./terminalkey')
                terminalpsw_node = xmlparams.find('./terminalpsw')
                terminalkey = terminalkey_node.text if terminalkey_node is not None else ''
                terminalpsw = terminalpsw_node.text if terminalpsw_node is not None else ''

                result = tinkoffapi.check_payment(terminalkey, terminalpsw, p['externalid'])

                logger.info(f"check payment result {result}")

                if result.success:
                    if result.status == PaymentStatus.NEW or result.status == PaymentStatus.FORM_SHOWED:
                        payment.set_in_pay(p['id'], p['info'], p['externalid'])
                    elif result.status == PaymentStatus.СANCELED:
                        payment.set_canceled(p['id'], p['info'], p['externalid'])
                    elif result.status == PaymentStatus.CONFIRMED:
                        payment.set_paid(p['id'], p['info'], p['externalid'])
                    elif result.status == PaymentStatus.REJECTED or result.status == PaymentStatus.AUTH_FAIL:
                        payment.set_fraud(p['id'], p['info'], p['externalid'])
                    else:
                        payment.set_canceled(p['id'], p['info'], p['externalid'])
                else:
                    payment.set_fraud(p['id'], p['info'], p['externalid'])
            except Exception as error:
                logger.info(f"payment {p['id']} exception {error}")

TestPaymentModule().Process()
