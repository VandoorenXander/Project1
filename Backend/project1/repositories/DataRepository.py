from .Database import Database


class DataRepository:
    @staticmethod
    def json_or_formdata(request):
        if request.content_type == 'application/json':
            gegevens = request.get_json()
        else:
            gegevens = request.form.to_dict()
        return gegevens

    @staticmethod
    def read_sens():
        sql = "SELECT * from Devices where Type ='Sensor'"
        return Database.get_rows(sql)

    @staticmethod
    def update_sens_read(sensorid,waarde):
        params=[waarde,sensorid]
        sql="INSERT INTO Meetwaarden (value,Devices_deviceid) Values (%s,%s);"
        Database.execute_sql(sql,params)

    @staticmethod
    def read_all_data():
        sql="SELECT * from Meetwaarden as M left join Devices as D on M.devices_deviceid = D.deviceid order by M.datum desc limit 50"
        return Database.get_rows(sql)

    @staticmethod
    def read_data_sens(id):
        sql="SELECT * from Meetwaarden as M left join Devices as D on M.devices_deviceid = D.deviceid  WHERE M.devices_deviceid = %s"
        params=[id]
        return Database.get_rows(sql,params)
    @staticmethod
    def read_status_lamp_by_id(id):
        sql = "SELECT * from lampen WHERE id = %s"
        params = [id]
        return Database.get_one_row(sql, params)

    @staticmethod
    def update_status_lamp(id, status):
        sql = "UPDATE lampen SET status = %s WHERE id = %s"
        params = [status, id]
        return Database.execute_sql(sql, params)

    @staticmethod
    def update_status_alle_lampen(status):
        sql = "UPDATE lampen SET status = %s"
        params = [status]
        return Database.execute_sql(sql, params)

    @staticmethod
    def get_last_feed_time():
        sql = ''

