from openai import OpenAI
import os
import json
from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import pipeline
import torch
from transformers import logging

class OpenSourceAIModel:
    def __init__(self, model_name="allenai/MolmoE-1B-0924"):
        # Initialize the tokenizer and the model
        token = os.getenv("$OPENSOURCE_TOKEN$")
        
        logging.set_verbosity_info()

        print("Initializing tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, token=token)
        print("Initializing model, this will take a while...")
        self.model = AutoModelForCausalLM.from_pretrained(model_name, token=token, trust_remote_code=True)
        self.messages = []
        
    def generate(self, max_new_tokens = 1000, temperature = 0.7):
        # Prepare conversation by concatenating system, user and assistant messages
        conversation_history = ""
        for message in self.messages:
            role = message['role']
            content = message['content']
            if role == "system":
                conversation_history += f"System: {content}\n"
            elif role == "user":
                conversation_history += f"User: {content}\n"
            elif role == "assistant":
                conversation_history += f"Assistant: {content}\n"
        
        # Tokenize the full conversation history for input
        
        self.tokenizer.add_special_tokens({"pad_token": '[PAD]'})
        encoded_inputs = self.tokenizer(conversation_history, return_tensors="pt", truncation=True, padding=True)
        input_ids = encoded_inputs['input_ids']
        attention_mask = encoded_inputs["attention_mask"]
        outputs = self.model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            do_sample=True,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            pad_token_id = self.tokenizer.pad_token_id
        )
        
        # Decode and add model output to conversation history
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        self.messages.append({"role": "assistant", "content": response})
        
        return response, "finish"
    
    def clear_conversation_history(self):
        self.messages = []

class AIModel:
    def __init__(self, api_key=None):
        print(os.environ)
        self.client = OpenAI(api_key=os.getenv("$OPENAI_API_KEY$", None))
        self.messages = []

    def generate(self, max_tokens=4096, temperature=0.7):
        response = self.client.chat.completions.create(
            model = 'gpt-4o',
            messages = self.messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        return response.choices[0].message.content.strip(), response.choices[0].finish_reason