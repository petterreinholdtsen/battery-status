# Collect battery status ever 10 minutes
*/10 * * * *     root    if [ -x /usr/sbin/battery-status-collect ]; then /usr/sbin/battery-status-collect ; fi
