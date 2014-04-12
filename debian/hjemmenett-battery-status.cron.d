# Collect battery status ever 10 minutes
*/10 * * * *     root    if [ -x /usr/sbin/collect-battery-status ]; then /usr/sbin/collect-battery-status ; fi
