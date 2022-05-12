import {useEffect, useRef, useState} from "react";
import axios from "axios";
import {renderCellExpand} from "../components/Results";

const COLS = [
    { field: 'id', headerName: 'ID', width: 70 },
    { field: 'title', headerName: 'Movie Name', width: 200 },
    { field: 'rating', headerName: 'Avg Rating', width: 100, valueGetter: (params) => params.value.toFixed(4) },
    { field: 'no_of_ratings', headerName: 'Num of Ratings', width: 140 },
    { field: 'correlation', headerName: 'Correlation', width: 100, valueGetter: (params) => params.value?.toFixed(4)  },
    { field: 'genres', headerName: 'Genres', width: 200,  valueGetter: (params) => params.value.join(', '),  renderCell: renderCellExpand},
    { field: 'original_language', headerName: 'Language', width: 90},
    { field: 'overview', headerName: 'Description', width: 410,   renderCell: renderCellExpand},
];



const API_URL = "http://127.0.0.1:80"

export const useRecommenderSystem = () => {
    const [collabMovies, setCollabMovies] = useState([]);
    const [collabUsers, setCollabUsers] = useState([]);
    const [contentBasedMovies, setContentBasedMovies] = useState([]);
    const [contentBasedUsers, setContentBasedUsers] = useState([]);
    const [modelType, setModelType] = useState("KNN");
    const [recommenderType, setRecommenderType] = useState("collaborative");
    const [userOrMovieName, setUserOrMovieName] = useState("");
    const [searchByUser, setSearchByUser] = useState(false);
    const [error, setError] = useState(false);
    const [results, setResults] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [cols, setCols] = useState(COLS);
    const predictionPromiseRef = useRef()


    const getMovies = async()=>{
        const responseCBMovies  = await axios.get(`${API_URL}/movies/contentbased`)
        const responseCMovies  = await axios.get(`${API_URL}/movies/collaborative?&model=${modelType}`)
        // const responseCBUsers  = await axios.get(`${API_URL}/users/contentbased`)
        const responseCUsers  = await axios.get(`${API_URL}/users/collaborative?&model=${modelType}`)
        // console.log(responseCMovies);
        setCollabMovies(responseCMovies.data.movies?.sort())
        setContentBasedMovies(responseCBMovies.data.movies?.sort())
        setCollabUsers(responseCUsers.data.users)
        // setContentBasedUsers(responseCBUsers.data.users)
    }

    const getPrediction = async()=>{
        clearTimeout(predictionPromiseRef.current)
        if (userOrMovieName.toString().length > 0){
            setIsLoading(true)
            let response
            try {
                response = await axios.get(`${API_URL}/${recommenderType}/${userOrMovieName}?user=${ searchByUser ? 'true' : 'false'}&model=${modelType}`)
                // console.log( response);
                if (response.data.success) {
                    const preds = response.data.prediction.map(pred => ({...pred,  ...pred.more_info}))
                    setResults(preds)
                    const newCols = COLS
                    if (response.data?.prediction.length > 0) {
                        if (response.data?.prediction?.[0].hasOwnProperty('similarity')) {
                            cols[4].headerName = "Similarity";
                            cols[4].field = "similarity"
                        } else if (response.data?.prediction?.[0].hasOwnProperty('distance')) {
                            cols[4].headerName = "Distance"
                            cols[4].field = "distance"
                        } else {
                            cols[4].headerName = "Correlation"
                            cols[4].field = "correlation"
                        }
                    }
                    setCols(newCols)
                }
            }catch (e) {
                console.log(e);
            }
            setError(!response?.data?.success)
            setIsLoading(false)
        }
    }

    useEffect(() => {
       getMovies()
    }, []);

    useEffect(()=>{
        if (recommenderType === "collaborative"){
            setModelType('KNN')
        }else {
            setModelType('CSR correlation matrix')
            setSearchByUser(false)
        }

    }, [recommenderType])

    useEffect(()=>{
        predictionPromiseRef.current = setTimeout(getPrediction, 350)
    }, [userOrMovieName])


    return {
        validUsers: recommenderType === "collaborative" ? collabUsers : contentBasedUsers,
        validMovies: recommenderType === "collaborative" ? collabMovies : contentBasedMovies,
        setSearchByUser,
        error,
        results,
        isLoading,
        cols,
        // validList,
        searchByUser,
        modelType,
        setModelType,
        recommenderType,
        setRecommenderType,
        userOrMovieName,
        setUserOrMovieName
    }

};
