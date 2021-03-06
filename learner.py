import torch
import torch.nn as nn
import torch.optim as optim
from losses import *
import tqdm

class Learner:
    
    def __init__(self, model, criterion, optimizer, task_name):
        self.model = model
        self.criterion = criterion
        self.optimizer = optimizer
        self.task_name = task_name
        self.log_file = f"log_{task_name}.txt"
        
        with open(self.log_file, 'w') as f:
            pass
        
    def train(self, train_dl, valid_dl, device, num_epochs):
        
        for epoch in tqdm.tqdm(range(num_epochs)):
            print(f"Epoch: {epoch}")
            
            train_loss = self._one_pass_loss(train_dl, device)
            train_mAP = self._one_pass_mAP(train_dl, device)
            
            log_msg = f"Epoch: {epoch}, train loss: {train_loss}, train_mAP: {train_mAP}"
            self._log(log_msg)
            
            valid_loss = self._one_pass_loss(valid_dl, device, backwards=False)
            valid_mAP = self._one_pass_mAP(valid_dl, device)
            
            log_msg = f"Epoch: {epoch}, valid loss: {valid_loss}, valid_mAP: {valid_mAP}"
            self._log(log_msg)
            
            
    def _log(self, message):
        if message.endswith('\n') is False:
            message += '\n'
        
        print(message)
        with open(self.log_file, "a") as f:
            f.write(message)
            
    def _one_pass_loss(self, dl, device, backwards=True):
        self.model.to(device)
        
        if backwards is True:
            self.model.train()
        else:
            self.model.eval()
            
        total_loss = 0.0
        total = 0
        
        loop = tqdm.tqdm(dl, leave=True)
        
        for i, (IMG, LABEL) in enumerate(loop):
            IMG, LABEL = IMG.to(device), LABEL.to(device)
            out = self.model(IMG)
            out = out.to(device)
            loss = self.criterion(out, LABEL)
            print(f"Batch {i} loss: {loss.item()}")
            
            n = IMG.shape[0]
            total += n
            total_loss += loss.item() * n
            
            if backwards is True:
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()
                
        avg_loss = total_loss / total
        
        return avg_loss
    
    
    def _one_pass_mAP(self, dl, device):
        self.model.eval()
        pred_boxes, target_boxes = get_bboxes(dl, self.model, device)
        mAP = mean_average_precision(pred_boxes, target_boxes)
        
        return mAP
