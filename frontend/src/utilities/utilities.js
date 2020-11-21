const addZeroToNumStr = (num) => {
    return num < 10 ? `0${num}`: String(num);
}
const formatDate = (date) => {
    const curMonth = addZeroToNumStr(date.getMonth()+1);
    const curDate = addZeroToNumStr(date.getDate()); 
    return `${date.getFullYear()}-${curMonth}-${curDate}`;
}

const formatTime = (date) => {
    const curHour = addZeroToNumStr(date.getHours());
    const curMin = addZeroToNumStr(date.getMinutes());
    return `${curHour}:${curMin}`;
}

const toLocalTime = (date) =>{
    let localDate = new Date(date)
    // let localDate = new Date(date.getTime() - date.getTimezoneOffset()*60*1000)
    return localDate
}

const constructDate = (dateString) => {
    // var dateString = "2010-08-09 01:02:03";
        // var reggie = /(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})/;
        var reggie = /(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})/;
        var dateArray = reggie.exec(dateString); 
        var dateObject = new Date(
            (+dateArray[1]),
            (+dateArray[2])-1, // Careful, month starts at 0!
            (+dateArray[3]),
            (+dateArray[4]),
            (+dateArray[5])
        );

        return dateObject;
}

export {
    formatDate,
    formatTime,
    constructDate,
    toLocalTime
}