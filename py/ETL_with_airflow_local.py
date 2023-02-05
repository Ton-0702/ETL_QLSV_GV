# import mysql.connector
import sqlalchemy as sql
import pandas as pd
import numpy as np
# from airflow import DAG
from datetime import timedelta
from datetime import datetime
# from airflow.operators.bash import BashOperator
# from airflow.operators.python import PythonOperator
# from airflow.utils.task_group import TaskGroup


def extract_mysql_consolidate(): # extract mysql and store to staging area on postgresql dạng table
    db_sv = sql.create_engine('mysql+mysqlconnector://root:toan123@localhost:3307/qlsv_gv') #root:toan123@localhost:3307  172.18.0.9:3307
    df_student = pd.read_sql_query("select * from qlsv_gv.student", db_sv)
    df_subject = pd.read_sql_query("select * from qlsv_gv.subject", db_sv)
    df_teacher = pd.read_sql_query("select * from qlsv_gv.teacher", db_sv)
    df_point = pd.read_sql_query("select * from qlsv_gv.point", db_sv)
    df_course_detail = pd.read_sql_query("select * from qlsv_gv.course_detail", db_sv)
    df_point.rename(columns = {'Score_tk1': 'score_tk1', 'Score_tk2': 'score_tk2', 'Score_tk3': 'score_tk3',\
        'Score_th1': 'score_th1', 'Score_th2': 'score_th2', 'Score_th3': 'score_th3', 'Score_gk': 'score_gk', 'Score_ck': 'score_ck'}, inplace = True)
    # print(df_point)
    print("============================ Hợp Nhất Dữ liệu Dataframe ===================================")
    # consolidate_data = pd.join([df_teacher, df_subject, df_course_detail, df_point, df_student], axis=1)
    consolidate_data = df_course_detail.join(df_teacher, lsuffix='_ref', rsuffix='_main')
    consolidate_data = consolidate_data.join(df_subject, lsuffix='_ref_course', rsuffix='_main')
    consolidate_data = df_point.join(consolidate_data, lsuffix='_ref_point', rsuffix='_main')
    consolidate_data = consolidate_data.join(df_student, lsuffix='_ref', rsuffix='_main')
    # print(consolidate_data)
    '''lưu ý: localhost:5432 để chạy test trên local, còn nếu chạy trên docker chuyển sang host container đó'''
    engine_postgre = sql.create_engine('postgresql://airflow:airflow@localhost:5432/qlsv_gv')  #airflow:airflow@localhost:5432  172.18.0.11:5432
    # # consolidate_data.to_csv('/home/ton/project_ca_nhan/DV_TAXI/ETL/file_csv_load_from_mysql/consolidate.csv', index=False)
    consolidate_data.to_sql('stg_qlsv_gv', engine_postgre, if_exists="replace", index=False)
    print("Import staging area success")

def transform_student():
    '''lưu ý: localhost:5432 để chạy test trên local, còn nếu chạy trên docker chuyển sang host container đó'''
    engine_postgre = sql.create_engine('postgresql://airflow:airflow@localhost:5432/qlsv_gv') #airflow:airflow@localhost:5432  172.18.0.11:5432
    data_stg_stu= pd.read_sql_query("SELECT student_id_main, student_name, birthday_stu, sex, academic_year, class_name\
                                 FROM public.stg_qlsv_gv", engine_postgre)
    data_stg_stu = data_stg_stu.dropna()
    data_stg_stu[['year', 'month', 'date']] = data_stg_stu['birthday_stu'].astype(str).str.split("-", expand=True)
    data_stg_stu.drop(['birthday_stu'], axis=1, inplace=True)
    data_stg_stu.rename(columns = {'student_id_main': 'student_id'}, inplace = True)
    data_stg_stu.sort_values(by=['student_id'])

    check_data_stu= pd.read_sql_query("SELECT COUNT(*) FROM public.dim_student", engine_postgre)

    if (check_data_stu['count'].values[0]) == 0:
        data_stg_stu.to_sql('dim_student', engine_postgre, if_exists="append", index=False)
    else:
        try:
            data_stg_stu_new = data_stg_stu[len(check_data_stu.index):]
            data_stg_stu_new.to_sql('dim_student', engine_postgre, if_exists="append", index=False)
        except:
            print("Already exists")
            pass
    # data_stg_stu.to_sql('dim_student', engine_postgre, if_exists="append", index=False)
    # print(data_stg)
    print("Import student success")

def transform_teacher():
    engine_postgre = sql.create_engine('postgresql://airflow:airflow@localhost:5432/qlsv_gv')
    data_stg_tea= pd.read_sql_query("SELECT teacher_id_main, name, level, birthday, nationality, degree, graduation_country, graduation_year\
                                 FROM public.stg_qlsv_gv", engine_postgre)
    data_stg_tea = data_stg_tea.dropna()
    data_stg_tea[['year', 'month', 'date']] = data_stg_tea['birthday'].astype(str).str.split("-", expand=True)
    data_stg_tea.drop(['birthday'], axis=1, inplace=True)
    data_stg_tea.rename(columns = {'teacher_id_main': 'teacher_id'}, inplace = True)
    data_stg_tea.sort_values(by=['teacher_id'])

    check_data_tea= pd.read_sql_query("SELECT COUNT(*) FROM public.dim_teacher", engine_postgre)
    if (check_data_tea['count'].values[0]) == 0:
        data_stg_tea.to_sql('dim_teacher', engine_postgre, if_exists="append", index=False)
    else:
        try:
            data_stg_tea_new = data_stg_tea[len(check_data_tea.index):]
            data_stg_tea_new.to_sql('dim_teacher', engine_postgre, if_exists="append", index=False)
        except:
            print("Already exists")
            pass
    # print(data_stg_tea)
    print("Import teacher success")

def transform_subject():
    engine_postgre = sql.create_engine('postgresql://airflow:airflow@localhost:5432/qlsv_gv')
    data_stg_sub= pd.read_sql_query("SELECT subject_id_main, name_subject, total_credit, program_semester\
                                        FROM public.stg_qlsv_gv", engine_postgre)
    data_stg_sub = data_stg_sub.dropna()
    data_stg_sub.rename(columns = {'subject_id_main': 'subject_id'}, inplace = True)
    data_stg_sub.sort_values(by=['subject_id'])
    # print(data_stg_type)

    check_data_sub= pd.read_sql_query("SELECT COUNT(*) FROM public.dim_subject", engine_postgre)
    if (check_data_sub['count'].values[0]) == 0:
        data_stg_sub.to_sql('dim_subject', engine_postgre, if_exists="append", index=False)
    else:
        try:
            data_stg_sub_new = data_stg_sub[len(check_data_sub.index):]
            data_stg_sub_new.to_sql('dim_subject', engine_postgre, if_exists="append", index=False)
        except:
            print("Already exists")
            pass
    # print(data_stg_tea)
    print("Import subject success")

def transform_course_type():
    engine_postgre = sql.create_engine('postgresql://airflow:airflow@localhost:5432/qlsv_gv')
    data_stg_type= pd.read_sql_query("SELECT type\
                                 FROM public.stg_qlsv_gv", engine_postgre)
    data_stg_type =  data_stg_type.drop_duplicates(subset=["type"], keep='first').reset_index(drop=True).reset_index()
    data_stg_type.rename(columns = {'index': 'type_id'}, inplace = True)
    data_stg_type = data_stg_type.dropna()

    check_data_type= pd.read_sql_query("SELECT COUNT(*) FROM public.dim_course_type", engine_postgre)
    if (check_data_type['count'].values[0]) == 0:
        data_stg_type.to_sql('dim_course_type', engine_postgre, if_exists="append", index=False)
    else:
        try:
            data_stg_type_new = data_stg_type[len(check_data_type.index):]
            data_stg_type_new.to_sql('dim_course_type', engine_postgre, if_exists="append", index=False)
        except:
            print("Already exists")
            pass
    print("Import course_type success")

def transform_point():
    engine_postgre = sql.create_engine('postgresql://airflow:airflow@localhost:5432/qlsv_gv') #, Score_tk2, Score_tk3, Score_th1, Score_th2, Score_th3, Score_gk, Score_ck
    data_stg_point= pd.read_sql_query("SELECT score_tk1, score_tk2, score_tk3, score_th1, score_th2, score_th3, score_gk, score_ck\
                                 FROM public.stg_qlsv_gv", engine_postgre)
    data_stg_point =  data_stg_point.reset_index()
    data_stg_point.rename(columns = {'index': 'point_id'}, inplace = True)
    # data_stg_point = data_stg_point.dropna()
    # print(data_stg_point)

    check_data_point= pd.read_sql_query("SELECT COUNT(*) FROM public.dim_point", engine_postgre)
    if (check_data_point['count'].values[0]) == 0:
        data_stg_point.to_sql('dim_point', engine_postgre, if_exists="append", index=False)
        data_old = pd.read_sql_query("SELECT * FROM public.stg_qlsv_gv", engine_postgre)
        data_stg_new = pd.concat([data_old, data_stg_point['point_id']], axis=1)
        # print(data_stg_new)
        data_stg_new.to_sql('stg_qlsv_gv', con=engine_postgre, if_exists='replace', index=False)
    else:
        try:
            data_stg_point_new = data_stg_point[len(check_data_point.index):]
            data_stg_point_new.to_sql('dim_point', engine_postgre, if_exists="append", index=False)

            data_old = pd.read_sql_query("SELECT * FROM public.stg_qlsv_gv", engine_postgre)
            data_stg_new = pd.concat([data_old, data_stg_point['point_id']], axis=1)
            # print(data_stg_new)
            data_stg_new.to_sql('stg_qlsv_gv', con=engine_postgre, if_exists='append', index=False)
        except:
            print("Already exists")
            pass
    # print(data_stg_point.index)

    # cập nhật staging area with point_id
    # try: 
    #     data_stg_point['point_id'].to_sql("stg_qlsv_gv", con=engine_postgre, if_exists='append', index=False)
    # except:
    #     data_old = pd.read_sql_query("SELECT * FROM public.stg_qlsv_gv", engine_postgre)
    #     data_stg_new = pd.concat([data_old, data_stg_point['point_id']], axis=1)
    #     # print(data_stg_new)
    #     data_stg_new.to_sql('stg_qlsv_gv', con=engine_postgre, if_exists='replace', index=False)

    # with engine_postgre.begin() as cn:
    #     sql = """
    #             ALTER TABLE stg_qlsv_gv ADD point_id
    #             UPDATE stg_qlsv_gv
    #             SET stg_qlsv_gv.point_id = t.col1
    #             FROM stg_qlsv_gv
    #             INNER JOIN dim_point"""

    #     cn.execute(sql)

    print("Import point and update staging success")

def transform_fact():
    engine_postgre = sql.create_engine('postgresql://airflow:airflow@localhost:5432/qlsv_gv')
    data_stg_fact= pd.read_sql_query("SELECT *\
                                 FROM public.stg_qlsv_gv", engine_postgre)
    df_stu_main = data_stg_fact.iloc[:,25:31].dropna()
    df_teacher_main = data_stg_fact.iloc[:,13:21].dropna()
    df_course_type = data_stg_fact.iloc[:,10:13].dropna()
    df_subject_main = data_stg_fact.iloc[:,21:25].dropna()
    df_point = pd.concat([data_stg_fact['point_id'], data_stg_fact.iloc[:,0:10]], axis=1) #[['point_id', 'subject_id', 'student_id_ref']]
    preDF = pd.merge(df_point, df_subject_main, left_on= 'subject_id', right_on='subject_id_main', how='inner')
    preDF = pd.merge(preDF, df_stu_main,  left_on= 'student_id_ref', right_on='student_id_main', how='inner')
    preDF = pd.merge(df_course_type, preDF,  left_on= 'subject_id_ref_course', right_on='subject_id_main', how='inner')
    preDF = pd.merge(df_teacher_main, preDF,  left_on= 'teacher_id_main', right_on='teacher_id_ref', how='inner')
    preDF.replace(['Lý thuyết', 'Thực hành'], [0, 1], inplace=True)
    
    preDF.drop(['teacher_id_main', 'subject_id', 'subject_id_main', 'student_id_main'], axis=1, inplace=True)
    preDF.rename(columns={'teacher_id_ref': 'teacher_id', 'subject_id_ref_course': 'subject_id', 'type': 'type_id', 'student_id_ref': 'student_id'}, inplace = True)

    # tạo id_report
    preDF =  preDF.reset_index()
    preDF.rename(columns = {'index': 'id_report'}, inplace = True)

    #aggregate data
    preDF['tb_tk'] = preDF[["score_tk1", "score_tk2", 'score_tk3']].mean(axis=1)
    preDF['tb_th'] = preDF[["score_th1", "score_th2", 'score_th3']].mean(axis=1)
    # preDF['total_subject_teach']
    preDF['total_subject_teach']= preDF.groupby('teacher_id')['subject_id'].count().reset_index()['subject_id']
    preDF['total_subject_teach'].replace(np.nan,0, inplace=True)
    result_DF = preDF[['id_report', 'teacher_id', 'subject_id', 'student_id', 'point_id', 'type_id', 'tb_tk', 'tb_th', 'total_subject_teach']]
    
    check_data_fact= pd.read_sql_query("SELECT COUNT(*) FROM public.fact_report", engine_postgre)
    if (check_data_fact['count'].values[0]) == 0:
        result_DF.to_sql('fact_report', engine_postgre, if_exists="append", index=False)
    else:
        try:
            result_DF = result_DF[len(check_data_fact.index):]
            result_DF.to_sql('fact_report', engine_postgre, if_exists="append", index=False)
        except:
            print("Already exists")
            pass
    print("Import fact table success")

# extract_mysql_consolidate()
# transform_student()
# transform_teacher()
# transform_course_type()
# transform_subject()
# transform_point()
# transform_fact()

default_dag = {
    'owner': 'Ton0702',
    'start_date': datetime(2023,2,4),
    'email': ['19447201.iuh@gmail.com'],
    'email_on_failure': False,
    'email_on_retry' : False,
    'retries' : 1,
    'retries_delay' : timedelta(minutes=3),
}

with DAG('ETL_qlsv_data', default_args= default_dag, description= 'Apache Airflow QLSV AND GV', schedule= timedelta(days=1)) as dag:
    extract_mysql = PythonOperator( # extract_load_into_staging_area_postgre
        task_id ='extract_sql',
        python_callable = extract_mysql_consolidate,
        dag=dag,
    )
    with DAG('ETL_qlsv_data', default_args= default_dag, description= 'Apache Airflow QLSV AND GV', schedule= timedelta(days=1)) as dag:
    extract_mysql = PythonOperator( # extract_load_into_staging_area_postgre
        task_id ='extract_sql',
        python_callable = extract_mysql_consolidate,
        dag=dag,
    )
    with TaskGroup("Dim_transfrom_to_postgresql", tooltip="Transform and load into postgre") as Dim_transfrom_to_postgresql: #tooltip cho biết nhiệm vụ của task group
        transform_src_student = PythonOperator( # transform_load_into_postgre
                    task_id ='transform_student',
                    python_callable = transform_student,
                    dag=dag,
        )
        transform_src_teacher = PythonOperator( # transform_load_into_postgre
                    task_id ='transform_teacher',
                    python_callable = transform_teacher,
                    dag=dag,
        )
        
        transform_src_course_type = PythonOperator( # transform_load_into_postgre
                    task_id ='transform_course_type',
                    python_callable = transform_course_type,
                    dag=dag,
        )

        transform_src_subject = PythonOperator( # transform_load_into_postgre
                    task_id ='transform_subject',
                    python_callable = transform_subject,
                    dag=dag,
        )
        
        #define task order
        [transform_src_student, transform_src_teacher, transform_src_course_type, transform_src_subject]

    Dim_transform_point_and_stg = PythonOperator( # transform vào postgres và cập nhật lại staging
        task_id ='transform_load_stg_and_postgre',
        python_callable = transform_point,
        dag=dag,
    )

    Fact_transform_table = PythonOperator( # transform vào bảng fact
        task_id ='transform_load_fact',
        python_callable = transform_fact,
        dag=dag,
    )

    extract_mysql >> transform_dim_qlsv >> Dim_transform_point_and_stg >> Fact_transform_table