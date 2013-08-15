# Collect battery status ever 15 minutes
*/15 * * * *     root    if [ -x /usr/sbin/collect-battery-status ]; then /usr/sbin/collect-battery-status ; fi
