"""
Visualisaion of a traceroute over a world map.

"""
import tkinter as tk
from matplotlib import animation, figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import cartopy.crs as ccrs
import requests

from traceroute import ping


import subprocess


def get_location(addr: str) -> (float, float):
    """Identify the global location of the supplied network address.
    
    The address is looked up on the geolocaion db
    """
    params = [
        'status',               # API status code
        'lat',
        'lon',
    ]
    resp = requests.get(
        'http://ip-api.com/json/' + addr,
        params = {'fields': ','.join(params)},
    )
    data = resp.json()
    try:
        lat = float(data['lat'])
        lon = float(data['lon'])
        if lat == 0.0 and lon == 0.0:
            raise ValueError
    except:
        return (None, None)
    
    return (lat, lon)


# GUI font constants
_FONT = 'Arial'
_FONT_SMALL = 14
_FONT_MEDIUM = 16
_FONT_LARGE = 18


class MapperGUI(tk.Tk):

    def __init__(self) -> None:
        
        super().__init__()
        self.wm_title('Route Mapper')

        # Generate the world map.
#        self.fig = figure.Figure(figsize=(10,5))
        self.fig = plt.figure(figsize=(10,5))
        self.ax = self.fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
        self.ax.set_global()
#        self.ax.stock_img()
        self.ax.coastlines()

        # Add the MatPlot figure to the TK root window.
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side = tk.TOP, fill = tk.BOTH)

        # Create our user controls
        self.controls = tk.Frame(self, padx=10, pady=10)
        self.controls.columnconfigure(0, weight=4)
        self.controls.columnconfigure(1, weight=2)
        self.controls.columnconfigure(2, weight=1)
        self.controls.columnconfigure(3, weight=1)

        self.dest_val = tk.StringVar()
        self.dest_entry = tk.Entry(
            self.controls,
            textvariable=self.dest_val,
            font=(_FONT, _FONT_MEDIUM),
        ).grid(row=0, column=1)

        self.trace_btn = tk.Button(
            self.controls,
            text="Trace",
            command=self._trace,
            font=(_FONT, _FONT_LARGE),
        ).grid(row=0, column=2)

        self.quit_btn = tk.Button(
            self.controls,
            text="Quit",
            command=self._quit,
            font=(_FONT, _FONT_LARGE),
        ).grid(row=0, column=3)

        self.controls.pack(fill=tk.X)

        self._reset()

        self.ani = animation.FuncAnimation(self.fig, self._traceroute, interval=2, save_count=20, blit=False)

    def _reset(self):
        self.last_lat, self.last_lon = (0.0, 0.0)
        self.ttl = 0
        self.dest_addr = None

    def _trace(self):
        self._reset()
        self.dest_addr = self.dest_val.get()
        self.ani.event_source.start()


    def _quit(self):
        self.destroy()
        exit(0)


    def _traceroute(self, event):
        self.ttl += 1
        if self.dest_addr is not None:
            ping_data = ping(self.dest_addr, ttl=self.ttl)
            if ping_data["dest"] is not None:
                lat, lon = get_location(ping_data["dest"])
                if lat is not None:
                    print(f"({self.ttl}: {self.last_lat},{self.last_lon})-({lat},{lon})")

    #                self.ax.plot([self.last_lon, lon], [self.last_lat, lat], transform=ccrs.PlateCarree())
                    self.ax.plot([self.last_lon, lon], [self.last_lat, lat], transform=ccrs.Geodetic())

                    self.last_lat = lat
                    self.last_lon = lon
                self.last_addr = ping_data["dest"]
                if self.ttl > 60 or ping_data["target"] == ping_data["dest"]:
                    self.ani.event_source.stop()


if __name__ == '__main__':
    print(get_location('www.google.com'))
    MapperGUI().mainloop()