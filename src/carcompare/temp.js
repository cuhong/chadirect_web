import React, {Component} from 'react';
import {Form, Button, Input, Dropdown} from 'semantic-ui-react';
import axios from 'axios';

var DEFAULT_REQUEST_URL = 'http://localhost:8000';

if (process.env.REACT_APP_INSCHECK_DEPLOYMENT_IP !== undefined)
    DEFAULT_REQUEST_URL = process.env.REACT_APP_INSCHECK_DEPLOYMENT_IP

class TestingForm extends Component {
    state = {
        auth_number: '',
        session_id: '',
        mname: '',
        prefix: '',
        suffix: '',
        phone_company: '',
        phone1: '',
        phone2: '',
        phone3: '',
        result_text: '',
        maker: 'all',
        car_no: '',
        next_col: 'car_name',
        car_name
:
    "QM5"
,
    car_register_year
        :
        "2016"
,
    coverage_bil
        :
        "가입"
,
    coverage_cac
        :
        "가입"
,
    coverage_mp
        :
        "2억원/2천만원"
,
    coverage_mp_list
        :
        "자동차상해"
,
    coverage_pdl
        :
        "2억원"
,
    coverage_umbi
        :
        "가입(2억원)"
,
    detail_car_name
        :
        "QM5 2.0 가솔린(2WD)"
,
    detail_option
        :
        "5인승 LE,오토,에어컨,ABS,AIR-D,IM(가솔린)"
,
    discount_and
        :
        "NO"
,
    discount_adas
        :
        "NO"
,
    discount_fca
        :
        "NO"
,
    discount_bb
        :
        "YES"
,
    discount_bb_month
        :
        "05"
,
    discount_bb_price
        :
        "10"
,
    discount_bb_year
        :
        "2015"
,
    discount_child
        :
        "YES"
,
    fetus
        :
        "NO"
,
    discount_child_day
        :
        "11"
,
    discount_child_month
        :
        "05"
,
    discount_child_year
        :
        "2013"
,
    discount_dist
        :
        "10,000km"
,
    discount_email
        :
        "YES"
,
    discount_mileage
        :
        "YES"
,
    discount_poverty
        :
        "NO"
,
    discount_premileage
        :
        "YES"
,
    discount_premileage_average
        :
        "24"
,
    discount_premileage_immediate
        :
        "24"
,
    discount_pubtrans
        :
        "YES"
,
    discount_pubtrans_cost
        :
        "12만원 이상"
,
    discount_safedriving
        :
        "YES"
,
    discount_safedriving_h
        :
        "NO"
,
    discount_safedriving_score
        :
        "100"
,
    discount_safedriving_h_score
        :
        "100"
,
    driver_day
        :
        "01"
,
    driver_month
        :
        "01"
,
    driver_year
        :
        "1991"
,
    driver2_day
        :
        "01"
,
    driver2_month
        :
        "01"
,
    driver2_year
        :
        "1991"
,
    manufacturer
        :
        "삼성"
,
    start_date
        :
        "2017-12-19"
,
    suffix
        :
        ""
,
    treaty_charge
        :
        "200만원"
,
    treaty_ers
        :
        "가입"
,
    treaty_range
        :
        "부부한정"
,
}

handleChange = (e, {name, value}) => this.setState({[name]: value})

handleCrawlRequest = async ({mname, prefix, suffix, phone_company, phone1, phone2, phone3}) => {
    const crawled_list = await Promise.all([
        axios.post(DEFAULT_REQUEST_URL + '/service-init/')
            .then(response => {
                this.setState({
                    session_id: response.data.session_id,
                });
                axios.post(DEFAULT_REQUEST_URL + '/send-auth-num/',
                    "session_id=" + response.data.session_id + "&name=" + mname + "&ssn_prefix=" + prefix + "&ssn_suffix=" + suffix + "&phone_company=" + phone_company + "&phone1=" + phone1 + "&phone2=" + phone2 + "&phone3=" + phone3)
                    .then(response => {
                        // this.setState({
                        //     session_id: response.data.session_id,
                        // });
                    })
                    .catch(error => {
                        console.log(error);
                    })
            })
            .catch(error => {
                console.log(error);
            })
    ]);
}

handleCrawlRequest2 = async () => {
    const {mname, prefix, suffix, phone_company, phone1, phone2, phone3} = this.state;
    const crawled_list = await Promise.all([
        axios.post(DEFAULT_REQUEST_URL + '/service-init/')
            .then(response => {
                this.setState({
                    session_id: response.data.session_id,
                });
                axios.post(DEFAULT_REQUEST_URL + '/send-auth-num/',
                    "session_id=" + response.data.session_id + "&name=" + mname + "&ssn_prefix=" + prefix + "&ssn_suffix=" + suffix + "&phone_company=" + phone_company + "&phone1=" + phone1 + "&phone2=" + phone2 + "&phone3=" + phone3)
                    .then(response => {
                        // this.setState({
                        //     session_id: response.data.session_id,
                        // });
                    })
                    .catch(error => {
                        console.log(error);
                    })
            })
            .catch(error => {
                console.log(error);
            })
    ]);
}

getDataByUrl = (url, param) => {
    return Promise.all([
        axios.post(DEFAULT_REQUEST_URL + url, param)
            .then(response => {
                return response.data;
            })
            .catch(error => {
                console.log(error);
            })
    ]);
}

handleSubmit = async () => {
    const {
        auth_number,
        session_id,
        mname,
        prefix,
        suffix,
        phone_company,
        phone1,
        phone2,
        phone3,
        result_text,
        start_date,
        manufacturer,
        car_no,
        car_name,
        car_register_year,
        detail_car_name,
        detail_option,
        coverage_pdl,
        coverage_bil,
        coverage_mp,
        coverage_cac,
        coverage_umbi,
        treaty_range,
        treaty_charge,
        driver_year,
        driver_month,
        driver_day,
        driver2_year,
        driver2_month,
        driver2_day,
        treaty_ers,
        coverage_mp_list,
        discount_mileage,
        discount_bb,
        discount_poverty,
        discount_email,
        discount_premileage,
        discount_safedriving,
        discount_safedriving_h,
        discount_pubtrans,
        discount_and,
        discount_adas,
        discount_fca,
        discount_child,
        discount_dist,
        fetus,
        discount_bb_year,
        discount_bb_month,
        discount_bb_price,
        discount_child_year,
        discount_child_month,
        discount_child_day,
        discount_pubtrans_cost,
        discount_safedriving_score,
        discount_safedriving_h_score,
        discount_premileage_average,
        discount_premileage_immediate,
    } = this.state;

    console.log(this.state)
    const resultList = await this.getDataByUrl('/result-list/', "session_id=" + session_id + "&double=N" +
        "&auth_number=" + auth_number +
        "&start_date=" + start_date + "&car_no=" + car_no +
        "&manufacturer=" + manufacturer +
        "&car_name=" + car_name + "&car_register_year=" + car_register_year + "&detail_car_name=" + detail_car_name + "&detail_option=" + detail_option +
        "&coverage_pdl=" + coverage_pdl + "&coverage_bil=" + coverage_bil + "&coverage_mp=" + coverage_mp + "&coverage_cac=" + coverage_cac + "&coverage_umbi=" + coverage_umbi +
        "&treaty_range=" + treaty_range + "&treaty_charge=" + treaty_charge +
        "&driver_year=" + driver_year + "&driver_month=" + driver_month + "&driver_day=" + driver_day +
        "&driver2_year=" + driver2_year + "&driver2_month=" + driver2_month + "&driver2_day=" + driver2_day +
        "&treaty_ers=" + treaty_ers + "&coverage_mp_list=" + coverage_mp_list +
        "&fetus=" + fetus +
        "&discount_mileage=" + discount_mileage + "&discount_bb=" + discount_bb + "&discount_poverty=" + discount_poverty + "&discount_email=" + discount_email + "&discount_premileage=" + discount_premileage + "&discount_safedriving=" + discount_safedriving + "&discount_safedriving_h=" + discount_safedriving_h + "&discount_pubtrans=" + discount_pubtrans + "&discount_and=" + discount_and + "&discount_adas=" + discount_adas + "&discount_fca=" + discount_fca + "&discount_child=" + discount_child + "&discount_dist=" + discount_dist +
        "&discount_bb_year=" + discount_bb_year + "&discount_bb_month=" + discount_bb_month + "&discount_bb_price=" + discount_bb_price +
        "&discount_child_year=" + discount_child_year + "&discount_child_month=" + discount_child_month + "&discount_child_day=" + discount_child_day + "&discount_pubtrans_cost=" + discount_pubtrans_cost + "&discount_safedriving_score=" + discount_safedriving_score + "&discount_safedriving_h_score=" + discount_safedriving_h_score + "&discount_premileage_average=" + discount_premileage_average + "&discount_premileage_immediate=" + discount_premileage_immediate);

    console.log(resultList[0])

    this.setState({result_text: resultList[0]})
}

handleSubmit3 = async () => {
    /*    const { auth_number, session_id } = this.state; */
    const {
        auth_number,
        session_id,
        mname,
        prefix,
        suffix,
        phone_company,
        phone1,
        phone2,
        phone3,
        result_text,
        start_date,
        manufacturer,
        car_no,
        car_name,
        car_register_year,
        detail_car_name,
        detail_option,
        coverage_pdl,
        coverage_bil,
        coverage_mp,
        coverage_cac,
        coverage_umbi,
        treaty_range,
        treaty_charge,
        driver_year,
        driver_month,
        driver_day,
        driver2_year,
        driver2_month,
        driver2_day,
        treaty_ers,
        coverage_mp_list,
        discount_mileage,
        discount_bb,
        discount_poverty,
        discount_email,
        discount_premileage,
        discount_safedriving,
        discount_safedriving_h,
        discount_pubtrans,
        discount_and,
        discount_adas,
        discount_fca,
        discount_child,
        discount_dist,
        fetus,
        discount_bb_year,
        discount_bb_month,
        discount_bb_price,
        discount_child_year,
        discount_child_month,
        discount_child_day,
        discount_pubtrans_cost,
        discount_safedriving_score,
        discount_safedriving_h_score,
        discount_premileage_average,
        discount_premileage_immediate,
    } = this.state;

    console.log(this.state)
    const resultList = await this.getDataByUrl('/cnc-result/', "session_id=" + session_id +
        "&auth_number=" + auth_number +
        "&start_date=" + start_date + "&car_no=" + car_no +
        "&manufacturer=" + manufacturer +
        "&car_name=" + car_name + "&car_register_year=" + car_register_year + "&detail_car_name=" + detail_car_name + "&detail_option=" + detail_option +
        "&coverage_pdl=" + coverage_pdl + "&coverage_bil=" + coverage_bil + "&coverage_mp=" + coverage_mp + "&coverage_cac=" + coverage_cac + "&coverage_umbi=" + coverage_umbi +
        "&treaty_range=" + treaty_range + "&treaty_charge=" + treaty_charge +
        "&driver_year=" + driver_year + "&driver_month=" + driver_month + "&driver_day=" + driver_day +
        "&driver2_year=" + driver2_year + "&driver2_month=" + driver2_month + "&driver2_day=" + driver2_day +
        "&treaty_ers=" + treaty_ers + "&coverage_mp_list=" + coverage_mp_list +
        "&fetus=" + fetus +
        "&discount_mileage=" + discount_mileage + "&discount_bb=" + discount_bb + "&discount_poverty=" + discount_poverty + "&discount_email=" + discount_email + "&discount_premileage=" + discount_premileage + "&discount_safedriving=" + discount_safedriving + "&discount_safedriving_h=" + discount_safedriving_h + "&discount_pubtrans=" + discount_pubtrans + "&discount_and=" + discount_and + "&discount_adas=" + discount_adas + "&discount_fca=" + discount_fca + "&discount_child=" + discount_child + "&discount_dist=" + discount_dist +
        "&discount_bb_year=" + discount_bb_year + "&discount_bb_month=" + discount_bb_month + "&discount_bb_price=" + discount_bb_price +
        "&discount_child_year=" + discount_child_year + "&discount_child_month=" + discount_child_month + "&discount_child_day=" + discount_child_day + "&discount_pubtrans_cost=" + discount_pubtrans_cost + "&discount_safedriving_score=" + discount_safedriving_score + "&discount_safedriving_h_score=" + discount_safedriving_h_score + "&discount_premileage_average=" + discount_premileage_average + "&discount_premileage_immediate=" + discount_premileage_immediate);

    console.log(resultList[0])

    this.setState({result_text: resultList[0]})
}


handleSubmit2 = async () => {
    const {auth_number, session_id, maker, start_date} = this.state;

    const resultList = await this.getDataByUrl('/get-carlist/', "session_id=" + session_id +
        "&auth_number=" + auth_number + "&maker=" + maker + "&start_date=" + start_date);
}

handleSubmit4 = () => {
    if (DEFAULT_REQUEST_URL == 'https://its-api.net/api') {
        // DEFAULT_REQUEST_URL='http://13.125.232.200/api/';
        DEFAULT_REQUEST_URL = 'http://localhost:8000';
    } else {
        DEFAULT_REQUEST_URL = 'https://its-api.net/api';
        // DEFAULT_REQUEST_URL='http://13.125.232.200/api/';
    }
}

handleSubmit5 = async () => {
    const {auth_number, session_id} = this.state;

    const resultList = await this.getDataByUrl('/shutdown-browser/', "session_id=" + session_id);
}

handleSubmit6 = async () => {
    const {car_no, start_date} = this.state;

    const resultList = await this.getDataByUrl('/get-carinfo/', "car_no=" + car_no + "&start_date=" + start_date);
}

handleSubmit7 = async () => {
    const {auth_number, session_id} = this.state;


    const resultList = await Promise.all([
        // axios.post(DEFAULT_REQUEST_URL +'/expolicy-find/',"session_id="+session_id+"&auth_number="+auth_number)
        // .catch(error => {
        //    console.log(error);

        axios.post(DEFAULT_REQUEST_URL + '/phone-auth-check/', "session_id=" + session_id + "&auth_number=" + auth_number + "&ci=Y")
            .then(response => {
                axios.post(DEFAULT_REQUEST_URL + '/expolicy-check/', "session_id=" + session_id)
                    .catch(error => {
                        console.log(error);
                    })
            })
            .catch(error => {
                console.log(error);
            })
    ]);
}

handleSubmit8 = async () => {
    const {next_col, manufacturer, car_name, car_register_year, detail_car_name, start_date} = this.state;

    const resultList = await this.getDataByUrl('/get-select-carlist/', "next_col=" + next_col +
        "&manufacturer=" + manufacturer + "&car_name=" + car_name + "&register_year=" + car_register_year + "&detail_name=" + detail_car_name + "&start_date=" + start_date);
}

handleSubmit9 = async () => {
    const {mname, prefix, suffix, phone_company, phone1, phone2, phone3, session_id} = this.state;
    const crawled_list = await Promise.all([
        axios.post(DEFAULT_REQUEST_URL + '/phone-auth-num/',
            "session_id=" + session_id + "&name=" + mname + "&ssn_prefix=" + prefix + "&ssn_suffix=" + suffix + "&phone_company=" + phone_company + "&phone1=" + phone1 + "&phone2=" + phone2 + "&phone3=" + phone3)
            .then(response => {
                this.setState({
                    session_id: response.data.session_id,
                });
            })
            .catch(error => {
                console.log(error);
            })
    ]);
}

render()
{
    const {auth_number} = this.state

    var today = new Date();
    var dd = today.getDate();
    var mm = today.getMonth() + 1;
    var yy = today.getFullYear();
    var date = yy + '-' + mm + '-' + dd

    if (this.state.coverage_mp_list == '자기신체손해') {
        var cover_list = <Dropdown placeholder='coverage_mp' name='coverage_mp' selection
                                   options={[{text: '1천5백만원/1천5백만원', value: '1천5백만원/1천5백만원'}, {
                                       text: '3천만원/1천5백만원',
                                       value: '3천만원/1천5백만원'
                                   }, {text: '5천만원/1천5백만원', value: '5천만원/1천5백만원'}, {
                                       text: '1억원/1천5백만원',
                                       value: '1억원/1천5백만원'
                                   }]} defaultValue='3천만원/1천5백만원' value={this.state.value}
                                   onChange={this.handleChange}/>;
    } else {
        var cover_list = <Dropdown placeholder='coverage_mp' name='coverage_mp' selection
                                   options={[{text: '1억원/2천만원', value: '1억원/2천만원'}, {
                                       text: '1억원/3천만원',
                                       value: '1억원/3천만원'
                                   }, {text: '2억원/2천만원', value: '2억원/2천만원'}, {text: '2억원/3천만원', value: '2억원/3천만원'}]}
                                   defaultValue='2억원/2천만원' value={this.state.value} onChange={this.handleChange}/>;
    }

    return (
        <div>
            <Button onClick={() => this.handleSubmit4()}> Server </Button>
            {DEFAULT_REQUEST_URL}
            <hr/>
            <Input placeholder='차량번호 입력' name='car_no' value={this.state.value} onChange={this.handleChange}/>
            <Button onClick={() => this.handleSubmit6()}> carinfo </Button>
            <br/>
            <Dropdown placeholder='next_col' name='next_col' value={this.state.value} selection
                      options={[{text: 'car_name', value: 'car_name'}, {
                          text: 'register_year',
                          value: 'register_year'
                      }, {text: 'detail_name', value: 'detail_name'}, {text: 'detail_option', value: 'detail_option'}]}
                      defaultValue='car_name' onChange={this.handleChange}/>
            <Button onClick={() => this.handleSubmit8()}> next_list </Button>
            <hr/>
            <Form onSubmit={this.handleCrawlRequest2}>
                <Input placeholder='이름' name='mname' value={this.state.value} onChange={this.handleChange}/>
                <Input placeholder='주민번호1' name='prefix' value={this.state.value} onChange={this.handleChange}/>
                <Input placeholder='주민번호2' name='suffix' value={this.state.value} onChange={this.handleChange}/>
                <br/>
                <Dropdown placeholder='통신사' name='phone_company' selection
                          options={[{text: 'SKT', value: '01'}, {text: 'KT', value: '02'}, {
                              text: 'LGU',
                              value: '03'
                          }, {text: 'SKT알뜰폰', value: '04'}, {text: 'KT알뜰폰', value: '05'}, {
                              text: 'LGU알뜰폰',
                              value: '06'
                          }]} value={this.state.value} onChange={this.handleChange}/>
                <Input placeholder='전화번호1' name='phone1' value={this.state.value} onChange={this.handleChange}/>
                <Input placeholder='전화번호2' name='phone2' value={this.state.value} onChange={this.handleChange}/>
                <Input placeholder='전화번호3' name='phone3' value={this.state.value} onChange={this.handleChange}/>
                <Button content='step1'/>
            </Form>
            <Button onClick={() => this.handleSubmit9()}> step1-1 </Button>
            <Button onClick={() => this.handleCrawlRequest({
                mname: "진영운",
                prefix: "830519",
                suffix: "1382614",
                phone_company: "03",
                phone1: "010",
                phone2: "2649",
                phone3: "6960"
            })}>step1 : 진영운 인증 요청</Button>
            <hr/>
            <Input placeholder='인증번호 입력' name='auth_number' value={auth_number} onChange={this.handleChange}/>
            <Button onClick={() => this.handleSubmit7()} content='step2'/>
            <Button onClick={() => this.handleSubmit()} content='step3'/>
            <Button onClick={() => this.handleSubmit3()}> restep3 </Button>
            <Input placeholder='제조사 입력' name='maker' value={this.state.value} defaultValue='all'
                   onChange={this.handleChange}/>
            <Button onClick={() => this.handleSubmit2()}> carlist </Button>
            <Button onClick={() => this.handleSubmit5()}> shutdown </Button>
            <Form onSubmit={this.handleSubmit}>
                <hr/>
                보험기간<Input placeholder='start_date' name='start_date' value={this.state.value} defaultValue={date}
                           onChange={this.handleChange}/>
                <br/>
                운전자범위
                <Dropdown placeholder='treaty_range' name='treaty_range' selection
                          options={[{text: '피보험자1인', value: '피보험자1인'}, {
                              text: '피보험자1인+지정1인',
                              value: '피보험자1인+지정1인'
                          }, {text: '누구나', value: '누구나'}, {text: '부부한정', value: '부부한정'}, {
                              text: '가족한정(형제자매 제외)',
                              value: '가족한정(형제자매 제외)'
                          }, {text: '가족한정+형제자매', value: '가족한정+형제자매'}]} defaultValue='부부한정' value={this.state.value}
                          onChange={this.handleChange}/>
                최연소운전자 생년월일
                <Input placeholder='driver_year' name='driver_year' defaultValue='1991' value={this.state.value}
                       onChange={this.handleChange}/>
                <Input placeholder='driver_month' name='driver_month' defaultValue='01' value={this.state.value}
                       onChange={this.handleChange}/>
                <Input placeholder='driver_day' name='driver_day' defaultValue='01' value={this.state.value}
                       onChange={this.handleChange}/>
                운전자2 생년월일
                <Input placeholder='driver2_year' name='driver2_year' defaultValue='1991' value={this.state.value}
                       onChange={this.handleChange}/>
                <Input placeholder='driver2_month' name='driver2_month' defaultValue='01' value={this.state.value}
                       onChange={this.handleChange}/>
                <Input placeholder='driver2_day' name='driver2_day' defaultValue='01' value={this.state.value}
                       onChange={this.handleChange}/>
                <br/>
                차량정보
                <Input placeholder='manufacturer' name='manufacturer' value={this.state.value} defaultValue='삼성'
                       onChange={this.handleChange}/>
                <Input placeholder='car_name' name='car_name' value={this.state.value} defaultValue='QM5'
                       onChange={this.handleChange}/>
                <Input placeholder='car_register_year' name='car_register_year' value={this.state.value}
                       defaultValue='2016' onChange={this.handleChange}/>
                <Input placeholder='detail_car_name' name='detail_car_name' value={this.state.value}
                       defaultValue='QM5 2.0 가솔린(2WD)' onChange={this.handleChange}/>
                <Input placeholder='detail_option' name='detail_option' value={this.state.value}
                       defaultValue='5인승 LE,오토,에어컨,ABS,AIR-D,IM(가솔린)+' onChange={this.handleChange}/>
                <br/>
                대인2
                <Dropdown placeholder='coverage_bil' name='coverage_bil' value={this.state.value} selection
                          options={[{text: '미가입', value: '미가입'}, {text: '가입', value: '가입'}]} defaultValue='가입'
                          onChange={this.handleChange}/>
                대물
                <Dropdown placeholder='coverage_pdl' name='coverage_pdl' selection
                          options={[{text: '2천만원', value: '2천만원'}, {text: '3천만원', value: '3천만원'}, {
                              text: '5천만원',
                              value: '5천만원'
                          }, {text: '1억원', value: '1억원'}, {text: '2억원', value: '2억원'}, {
                              text: '3억원',
                              value: '3억원'
                          }, {text: '5억원', value: '5억원'}]} defaultValue='2억원' value={this.state.value}
                          onChange={this.handleChange}/>
                <br/>
                자기신체손해
                <Dropdown placeholder='coverage_mp_list' name='coverage_mp_list' selection
                          options={[{text: '자기신체손해', value: '자기신체손해'}, {text: '자동차상해', value: '자동차상해'}, {
                              text: '미가입',
                              value: '미가입'
                          }]} defaultValue='자동차상해' value={this.state.value} onChange={this.handleChange}/>
                {cover_list}
                <br/>
                자기차량손해<Dropdown placeholder='coverage_cac' name='coverage_cac' selection
                                options={[{text: '미가입', value: '미가입'}, {text: '가입', value: '가입'}]} defaultValue='가입'
                                value={this.state.value} onChange={this.handleChange}/>
                무보험차상해<Dropdown placeholder='coverage_umbi' name='coverage_umbi' selection
                                options={[{text: '미가입', value: '미가입'}, {text: '가입(2억원)', value: '가입(2억원)'}]}
                                defaultValue='가입(2억원)' value={this.state.value} onChange={this.handleChange}/>
                <br/>
                긴급출동<Dropdown placeholder='treaty_ers' name='treaty_ers' selection
                              options={[{text: '미가입', value: '미가입'}, {text: '가입', value: '가입'}]}
                              value={this.state.value} defaultValue='가입' onChange={this.handleChange}/>
                물적할증금액<Dropdown placeholder='treaty_charge' name='treaty_charge' selection
                                options={[{text: '50만원', value: '50만원'}, {
                                    text: '100만원',
                                    value: '100만원'
                                }, {text: '150만원', value: '150만원'}, {text: '200만원', value: '200만원'}]}
                                defaultValue='200만원' value={this.state.value} onChange={this.handleChange}/>
                <hr/>
                마일리지<Dropdown placeholder='discount_mileage' name='discount_mileage' selection
                              options={[{text: 'NO', value: 'NO'}, {text: 'YES', value: 'YES'}]} defaultValue='YES'
                              value={this.state.value} onChange={this.handleChange}/>
                <Dropdown placeholder='discount_dist' name='discount_dist' selection
                          options={[{text: '2,000km', value: '2,000km'}, {
                              text: '3,000km',
                              value: '3,000km'
                          }, {text: '4,000km', value: '4,000km'}, {text: '5,000km', value: '5,000km'}, {
                              text: '6,000km',
                              value: '6,000km'
                          }, {text: '7,000km', value: '7,000km'}, {text: '8,000km', value: '8,000km'}, {
                              text: '9,000km',
                              value: '9,000km'
                          }, {text: '10,000km', value: '10,000km'}, {
                              text: '11,000km',
                              value: '11,000km'
                          }, {text: '12,000km', value: '12,000km'}, {
                              text: '13,000km',
                              value: '13,000km'
                          }, {text: '14,000km', value: '14,000km'}, {
                              text: '15,000km',
                              value: '15,000km'
                          }, {text: '16,000km', value: '16,000km'}, {
                              text: '17,000km',
                              value: '17,000km'
                          }, {text: '18,000km', value: '18,000km'}, {
                              text: '19,000km',
                              value: '19,000km'
                          }, {text: '20,000km', value: '20,000km'}]} defaultValue='10,000km' value={this.state.value}
                          onChange={this.handleChange}/>
                <br/>
                블랙박스<Dropdown placeholder='discount_bb' name='discount_bb' selection
                              options={[{text: 'NO', value: 'NO'}, {text: 'YES', value: 'YES'}]} defaultValue='YES'
                              value={this.state.value} onChange={this.handleChange}/>
                <Input placeholder='discount_bb_year' name='discount_bb_year' defaultValue='2015'
                       value={this.state.value} onChange={this.handleChange}/>
                <Input placeholder='discount_bb_month' name='discount_bb_month' defaultValue='05'
                       value={this.state.value} onChange={this.handleChange}/>
                <Input placeholder='discount_bb_price' name='discount_bb_price' defaultValue='10'
                       value={this.state.value} onChange={this.handleChange}/>
                <br/>
                자녀할인
                <Dropdown placeholder='discount_child' name='discount_child' selection
                          options={[{text: 'NO', value: 'NO'}, {text: 'YES', value: 'YES'}]} defaultValue='YES'
                          value={this.state.value} onChange={this.handleChange}/>
                <Input placeholder='discount_child_year' name='discount_child_year' defaultValue='2013'
                       value={this.state.value} onChange={this.handleChange}/>
                <Input placeholder='discount_child_month' name='discount_child_month' defaultValue='05'
                       value={this.state.value} onChange={this.handleChange}/>
                <Input placeholder='discount_child_day' name='discount_child_day' defaultValue='11'
                       value={this.state.value} onChange={this.handleChange}/>
                <br/>
                이메일할인<Dropdown placeholder='discount_email' name='discount_email' selection
                               options={[{text: 'NO', value: 'NO'}, {text: 'YES', value: 'YES'}]} defaultValue='YES'
                               value={this.state.value} onChange={this.handleChange}/>
                <br/>
                대중교통<Dropdown placeholder='discount_pubtrans' name='discount_pubtrans' selection
                              options={[{text: 'NO', value: 'NO'}, {text: 'YES', value: 'YES'}]} defaultValue='YES'
                              value={this.state.value} onChange={this.handleChange}/>
                <Dropdown placeholder='discount_pubtrans_cost' name='discount_pubtrans_cost' selection
                          options={[{text: '12만원 이상', value: '12만원 이상'}, {text: '24만원 이상', value: '24만원 이상'}]}
                          defaultValue='12만원 이상' value={this.state.value} onChange={this.handleChange}/>
                <br/>
                사고통보
                <Dropdown placeholder='discount_and' name='discount_and' selection
                          options={[{text: 'NO', value: 'NO'}, {text: 'YES', value: 'YES'}]} defaultValue='NO'
                          value={this.state.value} onChange={this.handleChange}/>
                <br/>
                차선이탈방지
                <Dropdown placeholder='discount_adas' name='discount_adas' selection
                          options={[{text: 'NO', value: 'NO'}, {text: 'YES', value: 'YES'}]} defaultValue='NO'
                          value={this.state.value} onChange={this.handleChange}/>
                <br/>
                전방충돌방지
                <Dropdown placeholder='discount_fca' name='discount_fca' selection
                          options={[{text: 'NO', value: 'NO'}, {text: 'YES', value: 'YES'}]} defaultValue='NO'
                          value={this.state.value} onChange={this.handleChange}/>
                <br/>
                안전운전(티맵)<Dropdown placeholder='discount_safedriving' name='discount_safedriving' selection
                                  options={[{text: 'NO', value: 'NO'}, {text: 'YES', value: 'YES'}]} defaultValue='YES'
                                  value={this.state.value} onChange={this.handleChange}/>
                <Input placeholder='discount_safedriving_score' name='discount_safedriving_score' defaultValue='100'
                       value={this.state.value} onChange={this.handleChange}/>
                <br/>
                안전운전(현대)<Dropdown placeholder='discount_safedriving_h' name='discount_safedriving_h' selection
                                  options={[{text: 'NO', value: 'NO'}, {text: 'YES', value: 'YES'}]} defaultValue='YES'
                                  value={this.state.value} onChange={this.handleChange}/>
                <Input placeholder='discount_safedriving_h_score' name='discount_safedriving_h_score' defaultValue='100'
                       value={this.state.value} onChange={this.handleChange}/>
                <br/>
                과거주행<Dropdown placeholder='discount_premileage' name='discount_premileage' selection
                              options={[{text: 'NO', value: 'NO'}, {text: 'YES', value: 'YES'}]} defaultValue='YES'
                              value={this.state.value} onChange={this.handleChange}/>
                <Input placeholder='discount_premileage_average' name='discount_premileage_average' defaultValue='24'
                       value={this.state.value} onChange={this.handleChange}/>
                <Input placeholder='discount_premileage_immediate' name='discount_premileage_immediate'
                       defaultValue='24' value={this.state.value} onChange={this.handleChange}/>
                <br/>
                서민할인<Dropdown placeholder='discount_poverty' name='discount_poverty' selection
                              options={[{text: 'NO', value: 'NO'}, {text: 'YES', value: 'YES'}]} defaultValue='NO'
                              value={this.state.value} onChange={this.handleChange}/>
                <br/>

                <Input type='text' name='result_text' value={this.state.value} onChange={this.handleChange}/>
            </Form>
        </div>
    )
}
}

export default TestingForm