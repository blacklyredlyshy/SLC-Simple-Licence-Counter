import json

from tkinter import Tk, Label, Button
from tkinter.font import Font
from typing import Union

from smb.SMBConnection import SMBConnection
from smb.base import SharedFile


class Config:
    """
    Loads app config from "config.json" file in working directory.
    """

    def __init__(self):
        with open('config.json') as f:
            config = json.load(f)

        # path
        self.actual_path = config['path']['actual_keys']
        self.activated_path = config['path']['activated_keys']

        # extensions
        self.actual_extension = config['extensions']['actual']
        self.activated_extension = config['extensions']['activated']

        # file server
        self.ip_address = config['file_server']['ip_address']
        self.target_dir = config['file_server']['target_dir']
        self.username = config['file_server']['username']
        self.password = config['file_server']['password']
        self.client_machine_name = config['file_server']['client_machine_name']


class Explorer:
    """
    Creates SMB connector, provides file system methods.
    """

    def __init__(self, username, password, client_machine_name, remote_ip):
        self.username = username
        self.password = password
        self.client_machine_name = client_machine_name
        self.remote_ip = remote_ip

    def create_connection(self) -> SMBConnection:
        """
        Creates SMB connection, provides file system methods.
        :return: SMB connection
        """
        return SMBConnection(
            username=self.username,
            password=self.password,
            my_name=self.client_machine_name,
            remote_name=self.remote_ip,
            use_ntlm_v2=True,
            is_direct_tcp=True
        )

    def list_path(self, service_name, path) -> Union[list[SharedFile], False]:
        """
        Shows directory content.
        :param service_name: server address (domain name or ip)
        :param path: path to target source
        :return: list of smb.baseSharedFile OR False if connection was failed
        """
        conn = self.create_connection()
        try:
            conn.connect(
                ip=self.remote_ip,
                port=445
            )
            content = conn.listPath(
                service_name=service_name,
                path=path
            )
            return content
        except Exception as e:
            print(e)
            return False
        finally:
            conn.close()



class LicenceCounter:
    """
    Provides keys files parsing functionality.
    """

    def __init__(self):
        self.conf = Config()
        self.explorer = Explorer(
            username=self.conf.username,
            password=self.conf.password,
            client_machine_name=self.conf.client_machine_name,
            remote_ip=self.conf.ip_address
        )

    def get_actual_keys(self) -> list[SharedFile]:
        """
        Loading actual keys files list from SMB connection.
        :return: list of smb.baseSharedFile objects
        """
        content = self.explorer.list_path(
            service_name=self.conf.target_dir,
            path=self.conf.actual_path
        )
        if content is False:
            return list()
        actual_keys_smb = self.filter_files_by_postfix(
            postfix=self.conf.actual_extension,
            files_list=content
        )
        return actual_keys_smb

    def get_consumed_keys(self) -> list[SharedFile]:
        """
        Loading consumed keys files list from SMB connection.
        :return: list of smb.baseSharedFile objects
        """
        content = self.explorer.list_path(
            service_name=self.conf.target_dir,
            path=self.conf.activated_path
        )
        if content is False:
            return list()
        consumed_keys_smb = self.filter_files_by_postfix(
            postfix=self.conf.activated_extension,
            files_list=content
        )
        return consumed_keys_smb

    @staticmethod
    def filter_files_by_postfix(files_list: list[SharedFile], postfix: str) -> list[SharedFile]:
        """
        Filter files_list according to postfix
        :param postfix: files postfix to be saved
        :param files_list: list of SharedFile objects
        :return: filtered list of SharedFile objects
        """
        item: SharedFile
        out_files_list = []

        for item in files_list:
            if item.filename.endswith(postfix):
                out_files_list.append(item)

        return out_files_list


class GUIApp:
    """
    Application main class.
    """
    params = {
        'title': 'Simple Licence Counter v0.2A',
        'geometry': '325x190+700+400',
        'resizable': False
    }

    background_style = {
        'bg': '#FFFFFF',
        'fg': '#000000',
        'font family': 'Segoe UI',
        'font weight': 'normal',
        'font size': 12
    }

    fields_style = {
        'bg': '#EEEEEE',
        'fg': '#000000',
        'font family': 'Segoe UI',
        'font weight': 'bold',
        'font size': 12
    }

    def __init__(self):
        self.root = Tk()
        self.root.title(
            self.params['title']
        )
        self.root.geometry(
            self.params['geometry']
        )
        self.root.resizable(
            width=self.params['resizable'],
            height=self.params['resizable']
        )
        self.root.config(
            bg=self.background_style['bg']
        )

        # setup widgets for window
        self.widgets = {

            'actual keys label': Label(
                text='Свободные ключи',
                bg=self.background_style['bg'],
                fg=self.background_style['fg'],
                font=Font(
                    family=self.background_style['font family'],
                    size=self.background_style['font size'],
                    weight=self.background_style['font weight']
                )
            ),

            'actual keys text': Label(
                text='N/a',
                bg=self.fields_style['bg'],
                fg=self.fields_style['fg'],
                font=Font(
                    family=self.fields_style['font family'],
                    size=self.fields_style['font size'],
                    weight=self.fields_style['font weight']
                )
            ),

            'consumed keys label': Label(
                text='Активированные',
                bg=self.background_style['bg'],
                fg=self.background_style['fg'],
                font=Font(
                    family=self.background_style['font family'],
                    size=self.background_style['font size'],
                    weight=self.background_style['font weight']
                )
            ),

            'consumed keys text': Label(
                text='N/a',
                bg=self.fields_style['bg'],
                fg=self.fields_style['fg'],
                font=Font(
                    family=self.fields_style['font family'],
                    size=self.fields_style['font size'],
                    weight=self.fields_style['font weight']
                )
            ),

            'update button': Button(
                text='Обновить',
                bg=self.fields_style['bg'],
                fg=self.fields_style['fg'],
                font=Font(
                    family=self.fields_style['font family'],
                    size=self.fields_style['font size'],
                    weight=self.fields_style['font weight']),
                command=self.update_keys
            ),

            'author label': Label(
                text='pavlenko.aa1@dns-shop.ru',
                bg=self.background_style['bg'],
                fg=self.background_style['fg'],
                font=Font(
                    family=self.background_style['font family'],
                    size=9,
                    weight=self.background_style['font weight']
                )
            )

        }

        """
        Widgets placing at window
        """

        # make a greed
        for column in range(2):
            self.root.columnconfigure(index=column, weight=1)
        for row in range(4):
            self.root.rowconfigure(index=row, weight=1)

        # place widgets at the greed
        self.widgets['actual keys label'].grid(row=0, column=0, padx=5, pady=5)
        self.widgets['actual keys text'].grid(row=0, column=1, ipadx=20, padx=5, pady=5)
        self.widgets['consumed keys label'].grid(row=1, column=0, padx=5, pady=5)
        self.widgets['consumed keys text'].grid(row=1, column=1, ipadx=20, padx=5, pady=5)
        self.widgets['update button'].grid(row=2, column=0, columnspan=4, ipadx=80, ipady=10, padx=5, pady=(5.0, 0.0))
        self.widgets['author label'].grid(row=3, column=0, columnspan=4, padx=5, pady=0)

    def run(self) -> None:
        """
        Run GUI application.
        :return: None
        """
        self.root.mainloop()

    def update_keys(self) -> None:
        """
        Update keys counters
        :return: None
        """
        lc = LicenceCounter()
        actual = lc.get_actual_keys()
        consumed = lc.get_consumed_keys()

        # reset fields
        self.widgets['actual keys text'].config(text='')
        self.widgets['consumed keys text'].config(text='')

        # fill fields
        self.widgets['actual keys text'].config(text=len(actual))
        self.widgets['consumed keys text'].config(text=len(consumed))


if __name__ == '__main__':
    GUIApp().run()
