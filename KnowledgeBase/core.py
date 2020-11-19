import tkinter as tk
from tkinter import *
from tkinter import ttk
from PIL import ImageTk, Image
import json
from copy import deepcopy
import pandas as pd


class Akinator:

	'''
	Class storing rule's conditions and result
	'''
	class Rule:
		def __init__(self, conditions, result):
			self.conditions = conditions
			self.result = result


	'''
	Constructor
	'''
	def __init__(self, gui_components):
		self.gui_components = gui_components

		self.NOT_FOUND_INDEX = -1
		self.RULE_APPROVED = 1
		self.RULE_IMCOMPLETE = 0
		self.RULE_DISAPPROVED = -1


	'''
	Loads start screen, data and prepares variables
	'''
	def load(self):

		# prepare gui components

		self.clear_gui()
		self.gui_components['START_BUTTON'].configure(command = self.run_akinator)
		self.gui_components['START_BUTTON'].place(x=320, y=200)

		self.gui_components['ANSWER_BUTTON'].configure(command = self.submit_answer)
		self.gui_components['NEW_GAME_BUTTON'].configure(command = self.load)
		self.gui_components['TEXT'].configure(text="Are you ready?", width=720)
		self.gui_components['TEXT'].pack(anchor='n', fill='x')

		# read data from json

		json_data = json.load(open('data/data.json', 'r', encoding='utf-8'))
		self.feature_values = json_data['feature_values']
		self.questions = json_data['questions']

		# read data from csv

		self.all_info = pd.read_csv('data/all_info.csv')
		for col in self.all_info.columns:
			self.all_info[col] = self.all_info[col].astype(str)

		# build main variables

		self.rules = []
		for json_rule in json_data['rules']:
			conditions = [tuple(x) for x in json_rule['conditions']]
			self.rules.append(self.Rule(conditions, tuple(json_rule['result'])))

		self.used_rules = []		
		self.target = 'name'
		self.target_stack = [[self.target, None]]
		self.context = []


	'''
	Clears gui
	'''
	def clear_gui(self):		
		for w in self.gui_components:
			self.gui_components[w].place_forget()


	'''
	Starts algorithm
	'''
	def run_akinator(self):
		self.clear_gui()
		self.gui_components['CONTEXT_LISTBOX'].configure(width=20, height=21)
		self.gui_components['CONTEXT_LISTBOX'].place(x=720-200, y=30)
		self.gui_components['CONTEXT_LISTBOX'].delete(0, 'end')
		self.main_loop()


	'''
	Shows image
	'''
	def display_image(self, name):
		image = Image.open('data/img/{}.jpg'.format(name))
		image = image.resize((250, 250), Image.ANTIALIAS)
		image = ImageTk.PhotoImage(image)
		self.gui_components['PHOTO_PANEL'].configure(image=image)
		self.gui_components['PHOTO_PANEL'].image = image
		self.gui_components['CHOICE_COMBOBOX'].place_forget()
		self.gui_components['ANSWER_BUTTON'].place_forget()
		self.gui_components['CONTEXT_LISTBOX'].place(x=720-200, y=30)
		self.gui_components['CONTEXT_LISTBOX'].update()
		self.gui_components['PHOTO_PANEL'].place(x=720//2-250//2, y=450//2-250//2, height=250, width=250)


	'''
	Reports about akinator's defeat
	'''
	def report_defeat(self):
		self.clear_gui()
		self.gui_components['TEXT'].configure(text = "Well, I have no answer", width=720)
		self.gui_components['TEXT'].pack(anchor='n', fill='x')
		self.gui_components['NEW_GAME_BUTTON'].place(x=720//2-50, y=450//2+250//2)
		self.display_image('defeat')


	'''
	Reports about akinator's win
	'''
	def report_win(self, ans):
		self.clear_gui()
		self.gui_components['TEXT'].configure(text="I think it's " + ans, width=720)
		self.gui_components['TEXT'].pack(anchor='n', fill='x')
		self.gui_components['NEW_GAME_BUTTON'].place(x=720//2-50, y=450//2+250//2)
		self.display_image(ans)


	'''
	Runs main algorithm's cycle
	'''
	def main_loop(self):

		assert len(self.target_stack) > 0, 'Error: empty target stack'
		curr_rule_ind = self.rule_search(self.target_stack[-1][0])

		# while we can find any rules for current target
		while curr_rule_ind != self.NOT_FOUND_INDEX:

			# check if approved
			if self.rule_check(curr_rule_ind) == self.RULE_APPROVED:

				# get rule
				curr_rule = self.rules[curr_rule_ind]	

				# add to context
				self.context.append(curr_rule.result)

				# update listbox
				self.gui_components['CONTEXT_LISTBOX'].insert(-1, '{}: {}'.format(*curr_rule.result))
				self.gui_components['CONTEXT_LISTBOX'].place(x=720-200, y=30)
				vals = self.gui_components['CONTEXT_LISTBOX'].get(0,tk.END)
				self.gui_components['CONTEXT_LISTBOX'].delete(0, tk.END)
				self.gui_components['CONTEXT_LISTBOX'].insert(tk.END, *vals)

				# remove current target (we know it's value)
				self.target_stack.pop()

				# if no more targets, report about win
				if len(self.target_stack) == 0:
					self.report_win(self.context[-1][1])
					return

			# if rule not approved, go for next (maybe for new target already)
			curr_rule_ind = self.rule_search(self.target_stack[-1][0])
				
		# if we run out of rules, but have some aux targets, go ask them
		if self.target_stack[-1][0] != self.target:
			self.ask_question(self.target_stack[-1][0])
		# else we've lost
		else:
			self.report_defeat()


	'''
	Predicts how much results you can get by going a specific way
	'''
	def predict_count(self, curr_target_feature, values):
		mod_values = []
		for value in values:
			mock_context = deepcopy(self.context)
			mock_context.append((curr_target_feature, value))

			mock_info = deepcopy(self.all_info)
			for cond in mock_context:
				mock_info = mock_info[mock_info[cond[0]] == cond[1]]
			mod_values.append(value + ' ({})'.format(len(mock_info)))
			
		return mod_values


	'''
	Asks person's a question
	'''
	def ask_question(self, curr_target_feature):	    
		self.clear_gui()
		self.gui_components['ANSWER_BUTTON'].place(x=320, y=200)		
		self.gui_components['TEXT'].configure(text=self.questions[curr_target_feature], width=720)
		self.gui_components['TEXT'].pack(anchor='n', fill='x')
		self.gui_components['CHOICE_COMBOBOX']['values'] = self.predict_count(curr_target_feature, self.feature_values[curr_target_feature])
		self.gui_components['CHOICE_COMBOBOX'].current(0)		
		self.gui_components['CHOICE_COMBOBOX'].place(x=150, y=210)
		self.gui_components['CONTEXT_LISTBOX'].configure(width=20, height=21)
		self.gui_components['CONTEXT_LISTBOX'].place(x=720-200, y=30)


	'''
	Gets person's answer to question
	'''
	def submit_answer(self):

		# receive selected answer from listbox
		answer = self.gui_components['CHOICE_COMBOBOX'].get()
		if '(' in answer:
			answer = answer[:answer.rfind('(') - 1]

		# get curr target and rule number (available when first item != init target)
		curr_target = self.target_stack[-1][0]
		curr_rule_ind = self.target_stack[-1][1]

		# if all ways can go only to nothing, end game
		pred = self.predict_count(curr_target, [answer])
		pred_count = pred[0][pred[0].rfind('('):]
		pred_count = int(pred_count[1:-1])
		if pred_count == 0:
			self.report_defeat()
			return

		# pop item that we're asking about
		self.target_stack.pop()

		# add received answer to context
		self.context.append((curr_target, answer))
		self.gui_components['CONTEXT_LISTBOX'].insert(0, '{}: {}'.format(curr_target, answer))
		self.gui_components['CONTEXT_LISTBOX'].place(x=720-200, y=30)
		vals = self.gui_components['CONTEXT_LISTBOX'].get(0,tk.END)
		self.gui_components['CONTEXT_LISTBOX'].delete(0, tk.END)
		self.gui_components['CONTEXT_LISTBOX'].insert(tk.END, *vals)

		# continue main loop
		self.main_loop()


	'''
	Searching for rule based on target
	'''
	def rule_search(self, curr_target_feature):	    
		for rule_ind in range(len(self.rules)):
			if rule_ind not in self.used_rules and self.rules[rule_ind].result[0] == curr_target_feature:
				return rule_ind
		return self.NOT_FOUND_INDEX


	'''
	Find in context list by feature name
	'''
	def find_in_context(self, feature):
		for ind, curr_context_condition in enumerate(self.context):
			if curr_context_condition[0] == feature:
				return ind
		return self.NOT_FOUND_INDEX


	'''
	Check if rule is correct
	'''
	def rule_check(self, rule_ind):
		rule = self.rules[rule_ind]
		for curr_rule_condition in rule.conditions:
			context_ind = self.find_in_context(curr_rule_condition[0])
			if context_ind == self.NOT_FOUND_INDEX:
				found = False
			else:
				found = True
				if curr_rule_condition[1] != self.context[context_ind][1]:
					self.used_rules.append(rule_ind)
					return self.RULE_DISAPPROVED
			if not found:
				self.target_stack.append([curr_rule_condition[0], rule_ind])
				return self.RULE_IMCOMPLETE

		self.used_rules.append(rule_ind)
		return self.RULE_APPROVED
