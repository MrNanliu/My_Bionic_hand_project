This script labels hand movement data based on finger distance thresholds:

* **Label 1 (Fist):** Both `Index_Dist` and `Mid_Dist` < 0.18.
* **Label 2 (Open):** Both `Index_Dist` and `Mid_Dist` > 0.28.
* **Label 0 (Rest/Transition):** Distances falling between the two thresholds.

It outputs a labelled `.csv` file and a `.png` plot visualising the results.