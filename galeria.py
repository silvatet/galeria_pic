import os
import threading
import time
import logging
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PIL import Image, ImageTk, ImageFilter, ImageOps
import cv2
import win32print
import win32ui
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# Configuração de logging
logging.basicConfig(filename="app.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Autenticação do Google Drive
gauth = GoogleAuth()
drive = None
try:
    gauth.LocalWebserverAuth()
    drive = GoogleDrive(gauth)
except Exception as e:
    logging.error(f"Erro na autenticação com o Google Drive: {e}")

# Classe para lidar com eventos do sistema de arquivos
class ImageHandler(FileSystemEventHandler):
    def __init__(self, app):
        self.app = app

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith((".png", ".jpg", ".jpeg")):
            logging.info(f"Nova imagem detectada: {event.src_path}")
            self.app.add_image(event.src_path)

# Classe principal do aplicativo
class ImageProcessingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Galeria PicBrand")
        self.processed_images = set()
        self.images_to_process = []
        self.observer = None
        self.camera = None
        self.upload_folder = None
        self.camera_index = 0

        # Configuração inicial da interface
        self.setup_ui()

    def setup_ui(self):
        """Configuração inicial da interface gráfica."""
        self.root.geometry("1000x700")
        self.root.configure(bg="#FFFFFF")

        # Título do aplicativo
        title_label = tk.Label(
            self.root, text="Galeria PicBrand", font=("Arial", 24, "bold"), bg="#4CAF50", fg="#FFFFFF"
        )
        title_label.pack(fill=tk.X, pady=10)

        # Configuração de abas
        self.tab_control = ttk.Notebook(self.root)

        # Criação das abas
        self.monitor_tab = ttk.Frame(self.tab_control)
        self.camera_tab = ttk.Frame(self.tab_control)
        self.upload_tab = ttk.Frame(self.tab_control)
        self.print_tab = ttk.Frame(self.tab_control)

        # Adicionando as abas ao controle
        self.tab_control.add(self.monitor_tab, text="Monitoramento")
        self.tab_control.add(self.camera_tab, text="Câmera")
        self.tab_control.add(self.upload_tab, text="Upload")
        self.tab_control.add(self.print_tab, text="Impressão")

        self.tab_control.pack(expand=1, fill="both")

        # Configuração de cada aba
        self.setup_monitor_tab()
        self.setup_camera_tab()
        self.setup_upload_tab()
        self.setup_print_tab()

    def setup_monitor_tab(self):
        """Configuração da aba de monitoramento."""
        ttk.Label(self.monitor_tab, text="Monitoramento de Imagens", font=("Arial", 16)).pack(pady=10)

        ttk.Button(self.monitor_tab, text="Selecionar Pasta para Monitoramento", command=self.select_folder,
                   width=40).pack(pady=10)

        self.image_listbox = tk.Listbox(self.monitor_tab, width=70, height=20, font=("Arial", 10))
        self.image_listbox.pack(pady=10)

        ttk.Label(self.monitor_tab, text="Escolha o efeito a aplicar:", font=("Arial", 12)).pack(pady=5)
        self.effect_combo = ttk.Combobox(self.monitor_tab, values=["Blur", "Gaussian Blur", "Emboss", "Sharpen", "Invert", "Grayscale", "Edge Enhance", "Contour"],
                                         font=("Arial", 10))
        self.effect_combo.set("Blur")
        self.effect_combo.pack(pady=5)

        ttk.Button(self.monitor_tab, text="Aplicar Efeito", command=self.apply_effect, width=40).pack(pady=10)

    def setup_camera_tab(self):
        """Configuração da aba de câmera."""
        ttk.Label(self.camera_tab, text="Captura de Imagem", font=("Arial", 16)).pack(pady=10)

        ttk.Button(self.camera_tab, text="Selecionar Câmera", command=self.select_camera, width=40).pack(pady=10)

        ttk.Button(self.camera_tab, text="Capturar Imagem da Câmera", command=self.capture_image, width=40).pack(
            pady=10)

        self.camera_preview = tk.Label(self.camera_tab, text="Pré-visualização da Câmera", bg="#EEEEEE", width=70,
                                       height=20, font=("Arial", 10))
        self.camera_preview.pack(pady=10)

    def setup_upload_tab(self):
        """Configuração da aba de upload."""
        ttk.Label(self.upload_tab, text="Upload de Imagens", font=("Arial", 16)).pack(pady=10)

        ttk.Button(self.upload_tab, text="Fazer Upload para o Google Drive", command=self.upload_to_drive,
                   width=40).pack(pady=10)

        self.upload_status = ttk.Label(self.upload_tab, text="Status: Nenhum upload realizado", font=("Arial", 12))
        self.upload_status.pack(pady=10)

    def setup_print_tab(self):
        """Configuração da aba de impressão."""
        ttk.Label(self.print_tab, text="Impressão de Imagens", font=("Arial", 16)).pack(pady=10)

        ttk.Button(self.print_tab, text="Selecionar Impressora", command=self.select_printer, width=40).pack(pady=10)

        self.printer_label = ttk.Label(self.print_tab, text="Impressora Selecionada: Nenhuma", font=("Arial", 12))
        self.printer_label.pack(pady=10)

        ttk.Button(self.print_tab, text="Imprimir Última Imagem", command=self.print_image, width=40).pack(pady=10)

    def select_folder(self):
        """Permite ao usuário selecionar uma pasta para monitoramento."""
        folder_path = filedialog.askdirectory()
        if not folder_path:
            messagebox.showwarning("Atenção", "Nenhuma pasta foi selecionada.")
            return

        if self.observer:
            self.observer.stop()
            self.observer.join()

        self.monitor_folder(folder_path)
        messagebox.showinfo("Sucesso", f"Pasta selecionada para monitoramento: {folder_path}")

    def monitor_folder(self, folder_path):
        """Inicia o monitoramento da pasta selecionada."""
        self.observer = Observer()
        event_handler = ImageHandler(self)
        self.observer.schedule(event_handler, folder_path, recursive=False)
        self.observer.start()

        # Thread para manter o monitoramento ativo
        thread = threading.Thread(target=self.keep_monitoring)
        thread.daemon = True
        thread.start()

    def keep_monitoring(self):
        """Mantém o monitoramento ativo."""
        try:
            while True:
                time.sleep(1)
        except Exception as e:
            logging.error(f"Erro no monitoramento: {e}")
            if self.observer:
                self.observer.stop()

    def add_image(self, image_path):
        """Adiciona uma imagem detectada à lista de imagens a serem processadas."""
        if image_path not in self.processed_images:
            self.images_to_process.append(image_path)
            self.image_listbox.insert(tk.END, image_path)
            self.processed_images.add(image_path)
            logging.info(f"Imagem adicionada à lista: {image_path}")

    def apply_effect(self):
        """Aplica um efeito selecionado às imagens na lista."""
        if not self.images_to_process:
            messagebox.showwarning("Atenção", "Nenhuma imagem para processar.")
            return

        effect = self.effect_combo.get()

        try:
            for image_path in self.images_to_process:
                img = Image.open(image_path)

                # Aplicação dos efeitos
                if effect == "Blur":
                    processed_img = img.filter(ImageFilter.BLUR)
                    processed_path = image_path.replace(".jpg", "_blurred.jpg")
                elif effect == "Gaussian Blur":
                    processed_img = img.filter(ImageFilter.GaussianBlur(radius=5))
                    processed_path = image_path.replace(".jpg", "_gaussian_blurred.jpg")
                elif effect == "Emboss":
                    processed_img = img.filter(ImageFilter.EMBOSS)
                    processed_path = image_path.replace(".jpg", "_emboss.jpg")
                elif effect == "Sharpen":
                    processed_img = img.filter(ImageFilter.SHARPEN)
                    processed_path = image_path.replace(".jpg", "_sharpen.jpg")
                elif effect == "Invert":
                    processed_img = ImageOps.invert(img.convert("RGB"))
                    processed_path = image_path.replace(".jpg", "_inverted.jpg")
                elif effect == "Grayscale":
                    processed_img = img.convert("L")
                    processed_path = image_path.replace(".jpg", "_grayscale.jpg")
                elif effect == "Edge Enhance":
                    processed_img = img.filter(ImageFilter.EDGE_ENHANCE)
                    processed_path = image_path.replace(".jpg", "_edge_enhanced.jpg")
                elif effect == "Contour":
                    processed_img = img.filter(ImageFilter.CONTOUR)
                    processed_path = image_path.replace(".jpg", "_contour.jpg")
                else:
                    messagebox.showerror("Erro", "Efeito desconhecido selecionado.")
                    return

                processed_img.save(processed_path)
                logging.info(f"{effect} aplicado em {processed_path}")

            messagebox.showinfo("Sucesso", f"Efeito {effect} aplicado com sucesso!")
        except Exception as e:
            logging.error(f"Erro ao aplicar efeito {effect}: {e}")

    def select_camera(self):
        """Permite ao usuário selecionar uma câmera disponível."""
        try:
            available_cameras = []
            for i in range(5):
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    available_cameras.append(i)
                    cap.release()

            if not available_cameras:
                messagebox.showerror("Erro", "Nenhuma câmera disponível encontrada.")
                return

            self.camera_index = available_cameras[0]
            messagebox.showinfo("Câmera Selecionada", f"Câmera {self.camera_index} selecionada com sucesso!")
        except Exception as e:
            logging.error(f"Erro ao selecionar câmera: {e}")

    def capture_image(self):
        """Captura uma imagem da câmera selecionada com um temporizador de 6 segundos."""
        try:
            self.camera = cv2.VideoCapture(self.camera_index)

            if not self.camera.isOpened():
                messagebox.showerror("Erro", "Não foi possível acessar a câmera.")
                return

            # Exibição da pré-visualização da câmera
            start_time = time.time()
            while time.time() - start_time < 6:
                ret, frame = self.camera.read()
                if ret:
                    cv2.imshow("Pré-visualização da Câmera", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            cv2.destroyWindow("Pré-visualização da Câmera")

            # Captura da imagem
            ret, frame = self.camera.read()
            if ret:
                folder_path = filedialog.askdirectory()
                if folder_path:
                    image_path = os.path.join(folder_path, f"image_{int(time.time())}.jpg")
                    cv2.imwrite(image_path, frame)
                    self.add_image(image_path)
                    logging.info(f"Imagem capturada e salva em: {image_path}")
            else:
                messagebox.showerror("Erro", "Falha ao capturar a imagem.")

            self.camera.release()
        except Exception as e:
            logging.error(f"Erro ao capturar imagem: {e}")
            messagebox.showerror("Erro", "Ocorreu um erro ao capturar a imagem.")

    def upload_to_drive(self):
        """Faz upload das imagens processadas para o Google Drive."""
        try:
            if not self.images_to_process:
                messagebox.showwarning("Atenção", "Nenhuma imagem para fazer upload.")
                return

            for image_path in self.images_to_process:
                file_name = os.path.basename(image_path)
                gfile = drive.CreateFile({'title': file_name})
                gfile.SetContentFile(image_path)
                gfile.Upload()
                logging.info(f"Upload concluído: {image_path}")

            self.upload_status.config(text="Status: Upload concluído com sucesso")
            messagebox.showinfo("Sucesso", "Upload concluído com sucesso!")
        except Exception as e:
            logging.error(f"Erro ao fazer upload: {e}")
            messagebox.showerror("Erro", "Falha ao fazer upload para o Google Drive.")

    def select_printer(self):
        """Permite ao usuário selecionar uma impressora padrão."""
        try:
            printer_name = win32print.GetDefaultPrinter()
            self.printer_label.config(text=f"Impressora Selecionada: {printer_name}")
            messagebox.showinfo("Sucesso", f"Impressora selecionada: {printer_name}")
        except Exception as e:
            logging.error(f"Erro ao selecionar impressora: {e}")
            messagebox.showerror("Erro", "Falha ao selecionar impressora.")

    def print_image(self):
        """Imprime a última imagem processada."""
        try:
            if not self.images_to_process:
                messagebox.showwarning("Atenção", "Nenhuma imagem para imprimir.")
                return

            image_path = self.images_to_process[-1]
            hprinter = win32print.OpenPrinter(win32print.GetDefaultPrinter())
            printer_info = win32print.GetPrinter(hprinter, 2)

            hdc = win32ui.CreateDC()
            hdc.CreatePrinterDC(printer_info['pPrinterName'])
            hdc.StartDoc(image_path)
            hdc.StartPage()

            bmp = Image.open(image_path)
            bmp = bmp.convert('RGB')

            dib = ImageWin.Dib(bmp)
            dib.draw(hdc.GetHandleOutput(), (0, 0, bmp.size[0], bmp.size[1]))

            hdc.EndPage()
            hdc.EndDoc()
            hdc.DeleteDC()

            logging.info(f"Imagem impressa: {image_path}")
            messagebox.showinfo("Sucesso", "Imagem impressa com sucesso!")
        except Exception as e:
            logging.error(f"Erro ao imprimir imagem: {e}")
            messagebox.showerror("Erro", "Falha ao imprimir imagem.")

# Execução do aplicativo
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessingApp(root)
    root.mainloop()
