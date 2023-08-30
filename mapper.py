"""
Visualisaion of a traceroute over a world map.

The things that you do when you are left unsupervised. This is an attempt
to put a visualisation on the standard traceroute/tracepath command with
the idea of trying to recreate those crazy scenes from the movies where they
trace the connection across the world in the hunt of their target.

Although all somewhat pointless, it is all in the nature of a bit of fun
and interesting playing with the quality of the IP geolocation data and
working out that everything is behind a CDN these days and connections
terminate all over the place.

Note:
    Enough time has been spend on this play project but the application is
    not very robust with bad data entry or network issues which will most
    likely cause it to hang or crash disgracefully. Some known issues for
    another day are:
        - The route tracing for www.ebay.com never ends
        - Parsing the physical address of some companies will fail
    
    Some items to address if we ever get back to this:
        - Line plotting is always one destination behind
        - Resizing of the map would be nice
"""
import tkinter as tk
from tkinter import messagebox
from matplotlib import animation, figure
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplcyberpunk
import cartopy.crs as ccrs
from geopy.geocoders import Nominatim
import requests

from traceroute import ping


def ip_location(addr: str) -> (float, float):
    """Identify the global location of the supplied network address.
    
    The address is looked up on the geolocaion db. Currently just uses
    ip-api.com as the database source.
    
    Note:
        Might be worth trying multiple sources to improve data quality
        at some stage.

    Paramteres
    ----------
    addr
        IP address string to find the geolocation of.

    Returns
    -------
    float
        Latitude reference of the geolocation (None on not found)
    float
        Longitude reference of the geolocation (None on not found) 
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


def osm_location(lat: float, lon: float) -> str:
    """Get street location data for the provided latitude and longatude.
    
    Open Street Map (OSM) is used to reverse geocode the provided latitude
    and longitude values into a street address.

    Parameters
    ----------
    lat
        Geolocation latitude reference
    long
        Geolocation longitude reference

    Returns
    -------
    str
        Structured string containing the street address of the geocode
    """
    address = geolocator.reverse(f"{lat}, {lon}").raw["address"]
    #print(f"ADDRESS => {address}")
    street = address.get("house_number", "") + " " + address["road"]
    town = address.get("town", address.get("city", "")) + ", " + address.get("state", address.get("state_district", ""))
    location = street.strip() + "\n" + town.strip() + "\n" + address.get("country", "")
    return location.strip()


# GUI font constants
_FONT = 'Arial'
_FONT_SMALL = 12
_FONT_MEDIUM = 16
_FONT_LARGE = 18

_BG_COLOUR = "grey10"
_TEXT_COLOUR = "cyan"

class MapperGUI(tk.Tk):
    """Display a Tk window to map a network traceroute across the world.
    
    Upon initalisation, displays a window that allows the user to enter
    destinations (targets) on the internet and the route tracing is plotted
    in real time on a map of the world.

    Geolocations are converted to physical addresses where possible and
    displayed.

    Note:
        There are many issues with handling error conditions and bad data
        entry which will probably cause this object to fail disgracefully.    
    """
    def __init__(self) -> None:
        
        super().__init__()
        self.wm_title('Route Mapper')
        self.protocol("WM_DELETE_WINDOW", self._quit)

        plt.style.use("cyberpunk")
        self.fig = plt.figure(figsize=(10,5), facecolor="black")
        self.ax = self.fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

        # Add the MatPlot figure to the TK root window.
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side = tk.TOP, fill = tk.BOTH)

        # Create our user controls
        self.controls = tk.Frame(self,
            padx=10, pady=10,
            background=_BG_COLOUR
        )
        self.controls.columnconfigure(0, weight=4)
        self.controls.columnconfigure(1, weight=1)
        self.controls.columnconfigure(2, weight=4)
        self.controls.columnconfigure(3, weight=1)

        self.location_text = tk.Text(
            self.controls,
            width=30,
            height=3,
            foreground=_TEXT_COLOUR,
            background=_BG_COLOUR,
            highlightbackground="grey25",
            state="disabled",
            font=('Courier', _FONT_SMALL),
        )
        self.location_text.grid(row=0, column=0)

        tk.Label(
            self.controls,
            text="Target:",
            foreground="grey",
            background=_BG_COLOUR,
            font=(_FONT, _FONT_MEDIUM),
        ).grid(row=0, column=1)

        self.dest_val = tk.StringVar()
        tk.Entry(
            self.controls,
            textvariable=self.dest_val,
            foreground=_TEXT_COLOUR,
            background="grey40",
            highlightbackground="grey25",
            font=(_FONT, _FONT_MEDIUM),
        ).grid(row=0, column=2)

        tk.Button(
            self.controls,
            text="Trace",
            command=self._trace,
            foreground=_TEXT_COLOUR,
            background=_BG_COLOUR,
            highlightbackground="grey25",
            font=(_FONT, _FONT_LARGE),
        ).grid(row=0, column=3)

        self.controls.pack(fill=tk.X)

        self._reset()
        self._redraw()
        self.ttl = 0

        self.ani = animation.FuncAnimation(self.fig, self._traceroute, interval=2, save_count=20, blit=False)


    # Clear the Matplotlib Axsis and redraw the screen.
    def _redraw(self):
        self.ax.cla()
        self.ax.set_global()
        self.ax.coastlines()
        self.location_text["state"] = "normal"
        self.location_text.delete('1.0', tk.END)
        self.location_text["state"] = "disabled"


    # Reset all processing data to its initial state.
    def _reset(self):
        self.dest_addr = None

        # To get our staring lat,lon we need our external IP
        my_ip = requests.get("https://checkip.amazonaws.com").text.strip()
        home_lat, home_lon = ip_location(my_ip)
        self.trace_lats = [home_lat]
        self.trace_lons = [home_lon]


    # Start a trace as an action to the Trace button.
    def _trace(self):
        self._reset()
        self.ttl = 0
        try:
            ping(self.dest_val.get())
            self.dest_addr = self.dest_val.get()
            self.ani.event_source.start()
        except:
            messagebox.showerror(
                title="Target Error",
                message=f"Destination {self.dest_val.get()} is not a known address!"
            )
            self.dest_val.set("")


    # Gracefully exit the Tkinter session (on window close).
    def _quit(self):
        self.quit()
        self.destroy()


    # Animation handler to perform the route trace and plot on the GUI.
    def _traceroute(self, event):
        self.ttl += 1
        if self.dest_addr is not None:
            ping_data = ping(self.dest_addr, ttl=self.ttl)
            if ping_data["dest"] is not None:
                lat, lon = ip_location(ping_data["dest"])
                if lat is not None:
                    print(f"({self.ttl}: ({lat},{lon})")
                    self.trace_lats.append(lat)
                    self.trace_lons.append(lon)

                    # Redraw the trace map with the extra location
                    self._redraw()
                    self.ax.plot(
                        self.trace_lons,
                        self.trace_lats,
                        transform=ccrs.PlateCarree(),
                        marker='o',
                        color='c',
                    )
                    mplcyberpunk.make_lines_glow()

                    # Update location status textbox
                    addr = osm_location(lat, lon)
                    self.location_text["state"] = "normal"
                    self.location_text.insert('1.0', addr)
                    self.location_text["state"] = "disabled"
                if self.ttl > 60 or ping_data["target"] == ping_data["dest"]:
                    self.ani.event_source.stop()
                    messagebox.showinfo(
                        title="Target Found!",
                        message=addr,
                        icon="warning",
                    )
                    self.dest_addr = None


if __name__ == '__main__':

    # This is global to save constantly creating it with each ping hop.
    geolocator = Nominatim(user_agent="Spy Tracker")

    MapperGUI().mainloop()
