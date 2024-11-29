import tkinter
import os
import random
from platform import system
from app_pet import Server
from tkinter.messagebox import askyesno
from tkinter import filedialog, ttk
import threading
from data import TokenExpirationPolicy
import customtkinter

CUSTOM_TK = 1.67

class Pet:
    def __init__(self):
        customtkinter.set_default_color_theme('dark-blue')
        self.root = customtkinter.CTk()
        self.delay = 200 # delay in ms
        self.pixels_from_right = 200 # change to move the pet's starting position
        self.pixels_from_bottom = 200 # change to move the pet's starting position
        self.move_speed = 6 # change how fast the pet moves in pixels
        self.server = Server()
        self.server_thread = threading.Thread(target=self.run_server)
        self.unsolved_event = []

        self.root.title("PrivAgent")
        self.current_mode = "pet"

        self.confirmation_setting_var = customtkinter.StringVar(value="on")
        self.pet_moving_setting_var = customtkinter.StringVar(value="on")
        self.expiration_setting_var = tkinter.StringVar()
        self.expiration_setting_var = customtkinter.StringVar(value="Expired at once")

        self.expiration_setting_choices = (
            "Expired at once",
            "Expired after 1 time",
            "Expired after 2 times",
            "Expired after 5 times",
            "Expired after 10 times",
            "Expired after 1 hour",
            "Expired after 2 hours"
        )

        self.expiration_setting_map = {
            "Expired at once": [TokenExpirationPolicy.EXPIRE_IN_TIMES, 1, 0],
            "Expired after 1 time": [TokenExpirationPolicy.EXPIRE_IN_TIMES, 2, 0],
            "Expired after 2 times": [TokenExpirationPolicy.EXPIRE_IN_TIMES, 3, 0],
            "Expired after 5 times": [TokenExpirationPolicy.EXPIRE_IN_TIMES, 6, 0],
            "Expired after 10 times": [TokenExpirationPolicy.EXPIRE_IN_TIMES, 11, 0],
            "Expired after 1 hour": [TokenExpirationPolicy.EXPIRE_AFTER_TIME, 1, 3600],
            "Expired after 2 hours": [TokenExpirationPolicy.EXPIRE_AFTER_TIME, 1, 7200]
        }

        # initialize frame arrays
        self.animation = dict(
            idle = [tkinter.PhotoImage(file=os.path.abspath('gifs/idle.gif'), format = 'gif -index %i' % i).zoom(9,9).subsample(5,5) for i in range(5)],
            idle_to_sleep = [tkinter.PhotoImage(file=os.path.abspath('gifs/idle-to-sleep.gif'), format = 'gif -index %i' % i).zoom(9,9).subsample(5,5) for i in range(8)],
            sleep = [tkinter.PhotoImage(file=os.path.abspath('gifs/sleep.gif'), format = 'gif -index %i' % i).zoom(9,9).subsample(5,5) for i in range(3)]*3,
            sleep_to_idle = [tkinter.PhotoImage(file=os.path.abspath('gifs/sleep-to-idle.gif'), format = 'gif -index %i' % i).zoom(9,9).subsample(5,5) for i in range(8)],
            walk_left = [tkinter.PhotoImage(file=os.path.abspath('gifs/walk-left.gif'), format = 'gif -index %i' % i).zoom(9,9).subsample(5,5) for i in range(8)],
            walk_right = [tkinter.PhotoImage(file=os.path.abspath('gifs/walk-right.gif'),format = 'gif -index %i' % i).zoom(9,9).subsample(5,5) for i in range(8)],
            wait_for_response = [tkinter.PhotoImage(file=os.path.abspath('gifs/wait_for_response.png')).zoom(9,9).subsample(5,5)]
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
        self.root.bind('<Button-1>', self.start_drag)
        self.root.bind('<B1-Motion>', self.drag)
        self.root.bind('<ButtonRelease-1>', self.stop_drag)
        # self.root.bind("<Button-1>", self.onLeftClick)
        self.root.bind("<Button-2>", self.onRightClick)
        self.root.bind("<Button-3>", self.onRightClick)
        self.root.bind("<Key>", self.onKeyPress)
        self.label = tkinter.Label(self.root,bd=0,bg='black') # borderless window
        # if system() != 'Windows':
        #     self.label.config(bg='systemTransparent')
        self.label.pack()
        
        screen_width = self.root.winfo_screenwidth() * CUSTOM_TK # width of the entire screen
        screen_height = self.root.winfo_screenheight() * CUSTOM_TK# height of the entire screen
        print("the screen width%d, the screen height %d", screen_width, screen_height)
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
                    if self.confirmation_setting_var.get() == "on":
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
        
    def toggle_confirmation(self):
        print("confirmation switch toggled, current value: ", self.confirmation_setting_var.get())
    
    def toggle_pet_moving(self):
        print("pet moving switch toggled, current value:", self.pet_moving_setting_var.get())

    def toggle_expiration_combobox(self, choice):
        print("combobox clicked:", choice)
        print(self.expiration_setting_map.keys())
        policy, token_times, token_time = self.expiration_setting_map[choice]
        self.server.action_service.set_policy(policy, token_times, token_time)

    def transform_pet_to_window(self):
        self.root.overrideredirect(False)
        self.root.attributes('-topmost', False)
        self.curr_width = 300
        self.curr_height = 350
        ws = self.root.winfo_screenwidth() * CUSTOM_TK
        hs = self.root.winfo_screenheight() * CUSTOM_TK
        x = (ws/2) - (CUSTOM_TK * self.curr_width/2)
        y = (hs/2) - (CUSTOM_TK * self.curr_height/2)

        self.root.geometry('%dx%d+%d+%d' % (self.curr_width, self.curr_height, x, y))
        self.root.update_idletasks()
        self.label.destroy()

        self.configuration_label = customtkinter.CTkLabel(master=self.root, text='User Configurations')
        self.configuration_label.pack(padx=20, pady=10)

        self.configuration_frame = customtkinter.CTkFrame(master=self.root, width=260, height=190)
        
        self.confirm_button_switch = customtkinter.CTkSwitch(master=self.configuration_frame, text='ask confirmation before action', command=self.toggle_confirmation, variable=self.confirmation_setting_var, onvalue="on", offvalue="off")
        self.confirm_button_switch.pack(padx=20, pady=10)
        self.pet_moving_button_switch = customtkinter.CTkSwitch(master=self.configuration_frame, text='keep pet moving', command=self.toggle_pet_moving, variable=self.pet_moving_setting_var, onvalue="on", offvalue="off")
        self.pet_moving_button_switch.pack(padx=20, pady=10)        

        self.expiration_frame = customtkinter.CTkFrame(master=self.configuration_frame, bg_color="transparent", fg_color="transparent")
        self.expiration_label = customtkinter.CTkLabel(master = self.expiration_frame, text='token expiration policy')
        self.expiration_label.pack(padx=20, pady=2, side='top')
        self.expiration_combobox = customtkinter.CTkComboBox(master=self.expiration_frame, values=self.expiration_setting_choices, command=self.toggle_expiration_combobox, variable=self.expiration_setting_var, width=200)        
        self.expiration_combobox.pack(padx=10, pady=2, side='left')

        self.expiration_frame.pack(pady=10)

        self.configuration_frame.pack(pady=10)

        self.mode_button = customtkinter.CTkButton(master=self.root,text='Return To Pet', corner_radius=8, command=self.transform_window_to_pet)
        self.mode_button.pack(padx=20, pady=10)

        self.log_download_button = customtkinter.CTkButton(master=self.root, text='Download Log', corner_radius=8, command=self.download_log)
        self.log_download_button.pack(padx=20, pady=2)

    def download_log(self):
        history = self.server.email_service.get_history_as_string()
        file_path = filedialog.asksaveasfilename(title="Save As", defaultextension=".txt", filetypes=[("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'wb') as file:
                    file.write(str.encode(history))
            except:
                print("some error happenening in the download process")

    def transform_window_to_pet(self):
        # transform from the window to the pet
        self.current_mode="pet"
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        screen_width = self.root.winfo_screenwidth() * CUSTOM_TK # width of the entire screen
        screen_height = self.root.winfo_screenheight() * CUSTOM_TK# height of the entire screen
        self.min_width = 10 # do not let the pet move beyond this point
        self.max_width = screen_width-110 # do not let the pet move beyond this point
        
        # change starting properties of the window
        self.curr_width = screen_width-self.pixels_from_right 
        self.curr_height = screen_height-self.pixels_from_bottom 
        self.root.geometry('%dx%d+%d+%d' % (100, 100, self.curr_width, self.curr_height))
        
        self.root.after(self.delay, self.update, 0, 'sleep')
        self.root.attributes('-fullscreen', False)

        self.configuration_label.destroy()
        self.configuration_frame.destroy()
        self.mode_button.destroy()
        self.log_download_button.destroy()
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
        if self.pet_moving_setting_var.get() == "off":
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
    
    def start_drag(self, event):
        if self.current_mode == "pet":
            self.is_dragging = True
            self.offset_x = event.x
            self.offset_y = event.y

    def drag(self, event):
        if self.current_mode == "pet" and self.is_dragging:
            new_x = self.root.winfo_pointerx() - self.offset_x
            new_y = self.root.winfo_pointery() - self.offset_y
            self.curr_width = new_x
            self.curr_height = new_y
            self.root.geometry(f'100x100+{int(self.curr_width)}+{int(self.curr_height)}')

    def stop_drag(self, event):
        if self.current_mode == "pet":
            self.is_dragging = False

    def quit(self):
        self.root.destroy()
        self.server_thread.join()


if __name__ == '__main__':
    print('Initializing your desktop pet...')
    print('To quit, right click on the pet')
    pet = Pet()
    pet.run()