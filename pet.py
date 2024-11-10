import tkinter
import os
import random
from platform import system
from app_pet import Server
from tkinter.messagebox import askyesno
import threading

class Pet:
    def __init__(self):
        self.root = tkinter.Tk() # create window
        self.delay = 200 # delay in ms
        self.pixels_from_right = 200 # change to move the pet's starting position
        self.pixels_from_bottom = 200 # change to move the pet's starting position
        self.move_speed = 6 # change how fast the pet moves in pixels
        self.server = Server()
        self.server_thread = threading.Thread(target=self.run_server)
        self.unsolved_event = []
        self.configurations = {
            "confirm":True,
            "pet_move":True,
        }
        self.current_mode = "pet"

        self.toggle_on_image = tkinter.PhotoImage(file=os.path.abspath("images/toggle_on.png")).subsample(10, 10)
        self.toggle_off_image = tkinter.PhotoImage(file=os.path.abspath("images/toggle_off.png")).subsample(10, 10)
        self.toggle_off_hover_image = tkinter.PhotoImage(file=os.path.abspath("images/toggle_off_hover.png")).subsample(10, 10)

        # initialize frame arrays
        self.animation = dict(
            idle = [tkinter.PhotoImage(file=os.path.abspath('gifs/idle.gif'), format = 'gif -index %i' % i) for i in range(5)],
            idle_to_sleep = [tkinter.PhotoImage(file=os.path.abspath('gifs/idle-to-sleep.gif'), format = 'gif -index %i' % i) for i in range(8)],
            sleep = [tkinter.PhotoImage(file=os.path.abspath('gifs/sleep.gif'), format = 'gif -index %i' % i) for i in range(3)]*3,
            sleep_to_idle = [tkinter.PhotoImage(file=os.path.abspath('gifs/sleep-to-idle.gif'), format = 'gif -index %i' % i) for i in range(8)],
            walk_left = [tkinter.PhotoImage(file=os.path.abspath('gifs/walk-left.gif'), format = 'gif -index %i' % i) for i in range(8)],
            walk_right = [tkinter.PhotoImage(file=os.path.abspath('gifs/walk-right.gif'),format = 'gif -index %i' % i) for i in range(8)],
            wait_for_response = [tkinter.PhotoImage(file=os.path.abspath('gifs/wait_for_response.png'))]
        )

        # window configuration
        if self.current_mode == "pet":
            self.root.overrideredirect(True) # remove UI

        if system() == 'Windows':
            self.root.wm_attributes('-transparent','black')
            pass
        else: # platform is Mac/Linux
            # https://stackoverflow.com/questions/19080499/transparent-background-in-a-tkinter-window
            self.root.wm_attributes('-transparent', True) # do this for mac, but the bg stays black
            self.root.config(bg='systemTransparent')
        
        self.root.attributes('-topmost', True) # put window on top
        self.root.bind("<Button-1>", self.onLeftClick)
        self.root.bind("<Button-2>", self.onRightClick)
        self.root.bind("<Button-3>", self.onRightClick)
        self.root.bind("<Key>", self.onKeyPress)
        self.label = tkinter.Label(self.root,bd=0,bg='black') # borderless window
        # if system() != 'Windows':
        #     self.label.config(bg='systemTransparent')
        self.label.pack()
        
        screen_width = self.root.winfo_screenwidth() # width of the entire screen
        screen_height = self.root.winfo_screenheight() # height of the entire screen
        self.min_width = 10 # do not let the pet move beyond this point
        self.max_width = screen_width-110 # do not let the pet move beyond this point
        
        # change starting properties of the window
        self.curr_width = screen_width-self.pixels_from_right
        self.curr_height = screen_height-self.pixels_from_bottom
        self.root.geometry('%dx%d+%d+%d' % (100, 100, self.curr_width, self.curr_height))
        
        self.server_thread.start()
        

    def run_server(self):
        self.server.run_server()

    def update(self, i, curr_animation):
        if self.current_mode == "pet":
            if curr_animation == 'wait_for_response':
                while self.server.event_queue.qsize() != 0:
                    event = self.server.event_queue.get(False)
                    if self.configurations["confirm"]:
                        self.unsolved_event.append(event)
                    else:
                        self.server.handler_queue.put(True)

            self.root.attributes('-topmost', True) # put window on top
            animation_arr = self.animation[curr_animation]
            frame = animation_arr[i]
            self.label.configure(image=frame)
            
            # move the pet if needed
            if curr_animation in ('walk_left', 'walk_right'):
                self.move_window(curr_animation)
            
            i += 1
            if i == len(animation_arr):
                # reached end of this animation, decide on the next animation
                next_animation = self.getNextAnimation(curr_animation)
                self.root.after(self.delay, self.update, 0, next_animation)
            else:
                self.root.after(self.delay, self.update, i, curr_animation)
        elif self.current_mode == "window":
            pass

    def onLeftClick(self, event):
        if len(self.unsolved_event) == 0:
            print("detected left click, nothing happened")
        else:
            event = self.unsolved_event.pop(0)
            answer = askyesno(message = self.server.confirm_service.get_confirmation_text(event.message))
            self.server.handler_queue.put(answer)

    def toggle_button(self, button_name: str, button: tkinter.Button):
        self.configurations[button_name] = not self.configurations[button_name]
        configuration = self.configurations[button_name]
        print("toggle the button to", configuration)
        if configuration:
            button.config(image=self.toggle_on_image)
        else:
            button.config(image=self.toggle_off_image)
        print("done the image change")

    def toggle(self):
        current_configuration = self.configurations["confirm"]
        self.configurations["confirm"] = not current_configuration
        
        if self.configurations["confirm"]:
            self.confirm_button.config(image=self.toggle_on_image)
        else:
            self.confirm_button.config(image=self.toggle_off_image)
        
    
    def transform_pet_to_window(self):
        # transform the pet to window
        self.root.overrideredirect(False)
        self.root.attributes('-topmost', False)
        self.curr_width = 300
        self.curr_height = 150
        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight()
        x = (ws/2) - (self.curr_width/2)
        y = (hs/2) - (self.curr_height/2)

        self.root.geometry("%dx%d+%d+%d" % (300, 150, x, y))
        self.label.destroy()

        self.window_frame = tkinter.Frame(self.root)
        self.window_frame.pack()

        self.confirm_button_frame = tkinter.Frame(self.window_frame, pady=10)
        self.confirm_button_label = tkinter.Label(self.confirm_button_frame, text='ask confirmation before action')
        self.confirm_button_label.pack(side='left', padx=10)
        if self.configurations["confirm"]:
            confirm_button_image = self.toggle_on_image
        else:
            confirm_button_image = self.toggle_off_image
        self.confirm_button = tkinter.Button(self.confirm_button_frame, image = confirm_button_image, bd=0, command=lambda: self.toggle_button("confirm", self.confirm_button))
        # self.confirm_button.bind('<Enter>', lambda: self.mouse_enter_button(self.confirm_button, "confirm"))
        # self.confirm_button.bind('<Leave>', lambda: self.mouse_leave_button(self.confirm_button, "confirm"))
        self.confirm_button.pack(side='right', padx=10)
        self.confirm_button_frame.pack()

        self.pet_moving_frame = tkinter.Frame(self.window_frame, pady=10)
        self.pet_moving_button_label = tkinter.Label(self.pet_moving_frame, text='keep pet moving')
        self.pet_moving_button_label.pack(side='left', padx=10)
        if self.configurations["pet_move"]:
            pet_moving_button_image = self.toggle_on_image
        else:
            pet_moving_button_image = self.toggle_off_image
        self.pet_moving_button = tkinter.Button(self.pet_moving_frame, image=pet_moving_button_image, bd=0, command = lambda: self.toggle_button("pet_move", self.pet_moving_button))
        self.pet_moving_button.pack(side='right', padx=10)
        self.pet_moving_frame.pack()

        self.mode_button_frame = tkinter.Frame(self.window_frame, pady=10)
        self.mode_button = tkinter.Button(self.mode_button_frame, text='Return To Pet Mode', command=self.transform_window_to_pet)
        self.mode_button.pack()
        self.mode_button_frame.pack()

    def mouse_enter_button(self, button, button_name):
        print("mouse enter")
        if not self.configurations[button_name]:
            button.image = self.toggle_off_hover_image

    def mouse_leave_button(self, button, button_name):
        print("mouse leave")
        if not self.configurations[button_name]:
            button.image = self.toggle_off_image

    def transform_window_to_pet(self):
        # transform from the window to the pet
        self.current_mode="pet"
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.curr_width = self.root.winfo_screenwidth() - self.pixels_from_right
        self.curr_height = self.root.winfo_screenheight() - self.pixels_from_bottom
        self.root.geometry('%dx%d+%d+%d' % (100, 100, self.curr_width, self.curr_height))
        self.root.after(self.delay, self.update, 0, 'sleep')
        self.root.attributes('-fullscreen', False)

        self.confirm_button.destroy()
        self.pet_moving_button.destroy()
        self.mode_button.destroy()
        self.window_frame.destroy()
        self.label = tkinter.Label(self.root,bd=0,bg='black') # borderless window
        self.label.pack()
    
    def onRightClick(self, event):
        if self.current_mode == "pet" and len(self.unsolved_event)==0:
            print("from pet to window")
            self.current_mode = "window"
            self.transform_pet_to_window()
        elif self.current_mode == "window":
            print("from window to pet")
            self.current_mode = "pet"
            self.transform_window_to_pet()


    def onKeyPress(self, event):
        if event.char in ('q', 'Q'):
            self.quit()
    
    
    def move_window(self, curr_animation):
        if curr_animation == 'walk_left':
            if self.curr_width > self.min_width:
                self.curr_width -= self.move_speed
            
        elif curr_animation == 'walk_right':
            if self.curr_width < self.max_width:
                self.curr_width += self.move_speed

        self.root.geometry('%dx%d+%d+%d' % (100, 100, self.curr_width, self.curr_height))
    

    def getNextAnimation(self, curr_animation):
        if not self.configurations['pet_move']:
            if self.server.event_queue.qsize() != 0:
                next_animation = {
                    'idle': 'idle_to_sleep',
                    'idle_to_sleep': 'wait_for_response',
                    'walk_left':'idle_to_sleep',
                    'walk_right':'idle_to_sleep',
                    'sleep':'wait_for_response',
                    'sleep_to_idle':'idle_to_sleep'
                }
                return next_animation[curr_animation]
            return 'sleep'
        else:
            if self.server.event_queue.qsize() != 0:
                next_animation = {
                    'idle': 'idle_to_sleep',
                    'idle_to_sleep': 'wait_for_response',
                    'walk_left':'idle_to_sleep',
                    'walk_right':'idle_to_sleep',
                    'sleep':'wait_for_response',
                    'sleep_to_idle':'idle_to_sleep'
                }
                return next_animation[curr_animation]

            if curr_animation == 'idle':
                return random.choice(['idle', 'idle_to_sleep', 'walk_left', 'walk_right'])
            elif curr_animation == 'idle_to_sleep':
                return 'sleep'
            elif curr_animation == 'sleep':
                return random.choice(['sleep', 'sleep_to_idle'])
            elif curr_animation == 'sleep_to_idle':
                return 'idle'
            elif curr_animation == 'walk_left':
                return random.choice(['idle', 'walk_left', 'walk_right'])
            elif curr_animation == 'walk_right':
                return random.choice(['idle', 'walk_left', 'walk_right'])
            elif curr_animation == 'wait_for_response':
                if len(self.unsolved_event) == 0:
                    return 'sleep_to_idle'
                else:
                    return 'wait_for_response'
         
    
    def run(self):
        self.root.after(self.delay, self.update, 0, 'sleep') # start on idle
        self.root.mainloop()
    
    
    def quit(self):
        self.root.destroy()
        self.server_thread.join()


if __name__ == '__main__':
    print('Initializing your desktop pet...')
    print('To quit, right click on the pet')
    pet = Pet()
    pet.run()