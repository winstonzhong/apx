# encoding: utf-8
'''
Created on 2017年7月5日

@author: winston
'''
import time

from django.db.transaction import atomic
from svmutil import svm_predict

from dcxj.tool_env import CmdProgress
from training.ligament import BaseLigament
from training.mpdfs import SingleConsumer


class TransactinUpdateHelper(object):
    def __init__(self, records, p_label, p_val, model_cls=None, index_1=None):
        d = {}
        if not isinstance(records[0], int):
            ids = map(lambda x:x.id, records)
        else:
            ids = records
        
        self.model_cls = model_cls or records[0].get_model_class()
        
        if index_1 is None:
            index_1 = self.model_cls.get_1_index()    
        for i in xrange(len(ids)):
            d.setdefault(ids[i], (p_label[i], p_val[i][index_1]))
        self.d = d
        
        
    
    @atomic(using='default', savepoint=True)
    def update(self):
        old = time.time()
        print "writing back to db:", len(self.d)
        cp = CmdProgress(len(self.d))
#         set_autocommit(False, 'abdb')
        cls = self.model_cls
        for k,(result, pval) in self.d.items():
#             k.result = result
#             k.pval = pval
#             k.save()
            cls.objects.filter(id=k).update(result=result, pval=pval)
            cp.update()
#         commit('abdb')
#         set_autocommit(True)
        print "seconds:", time.time() - old 

class AdvancedLigament(BaseLigament):
    @classmethod
    def predict_all(cls, l):
        df = SingleConsumer(cls_model=cls, records=l).run(enable_weight=False, prescaled=True)
        
        ids = df.id.tolist()
        del df['id']
        d = df.to_dict('split')
        
        x = d.get('data')
        y = d.get('index')
        
        m = cls.get_model()
        
        p_label, p_val, ACC = svm_predict(y, x, m, options="-q")
        
#         print ids
#         print p_label, p_val, ACC
        
        TransactinUpdateHelper(ids, p_label, ACC, cls.get_model_class(), 0).update()
        
        cls.update_pval(l)
        
        return p_label, p_val, ACC
        
#     @classmethod
#     def predict_today(cls):
# #         cls.get_model_class().write_today_all()
#         l = map(lambda x:cls(x), TP0.objects.filter(date=today(), abandoned=0))
#         cls.predict_all(l)