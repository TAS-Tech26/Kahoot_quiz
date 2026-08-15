// QuestionEditor.jsx


import MediaUploader from './MediaUploader'


export default function QuestionEditor({register, index, watch, setValue, setIsUploading}) {

    const currentMediaUrl = watch(`questions.${index}.media_url`)
    const currentMediaType = watch(`questions.${index}.media_type`)

    return (

        <div className = "flex flex-col gap-8 p-8 bg-btn-neutral border-4 border-ink shadow-brutal-lg">
            <div>
                <label className = "block font-mono font-bold text-2xl mb-4 uppercase tracking-tighter text-ink">
                    Question Text
                </label>

                <input
                    type = 'text'
                    {...register(`questions.${index}.text`, {required : true})}
                    className = "w-full bg-bg-base text-ink border-4 border-ink p-6 font-mono text-xl shadow-brutal-sm focus:outline-none focus:shadow-brutal-md transition-shadow placeholder:text-ink/50"
                    placeholder = "ENTER YOUR QUESTION HERE..."
                />
            </div>

            <div className = "grid grid-cols-2 gap-8">
                <div>
                    <label className = "block font-mono font-bold text-xl mb-4 uppercase tracking-tight text-ink">
                        Time Limit (Seconds)
                    </label>

                    <input
                        type = 'number'
                        placeholder = 'e.g. 10'
                        {...register(`questions.${index}.time_limit`, {required : true, valueAsNumber : true, min : 5, max : 600})}
                        className = "w-full bg-bg-base text-ink border-4 border-ink p-4 font-mono font-bold text-xl shadow-brutal-sm focus:outline-none focus:shadow-brutal-md transition-shadow placeholder:text-ink/40"
                    />
                </div>
                
                <div>
                    <label className = "block font-mono font-bold text-2xl mb-4 uppercase tracking-tighter text-ink">
                        Media (Optional)
                    </label>

                    <MediaUploader
                        currentMediaUrl = {currentMediaUrl}
                        currentMediaType = {currentMediaType}
                        setIsUploading = {setIsUploading}
                        onUploadSuccess = {(url, type) => {
                            setValue(`questions.${index}.media_url`, url)
                            setValue(`questions.${index}.media_type`, type)
                        }}
                        onRemove = {() => {
                            setValue(`questions.${index}.media_url`, null)
                            setValue(`questions.${index}.media_type`, null)
                        }}
                    />
                </div>
            </div>

            <div>
                <label className = "block font-mono font-bold text-2xl mb-6 uppercase tracking-tighter text-ink">
                    Answers (Check Correct)
                </label>

                <div className = "grid grid-cols-2 gap-6">
                    {[0, 1, 2, 3].map((choiceIndex) => (
                        <div
                            key = {choiceIndex}
                            className = "flex bg-bg-base border-4 border-ink shadow-brutal-sm focus-within:shadow-brutal-md transition-shadow"
                        >
                            <div className = "flex items-center justify-center p-4 border-r-4 border-ink bg-card-dark">
                                <input
                                    type = 'checkbox'
                                    {...register(`questions.${index}.choices.${choiceIndex}.is_correct`)}
                                    className = "h-8 w-8 cursor-pointer accent-brutal-green"
                                />
                            </div>

                            <input
                                type = 'text'
                                {...register(`questions.${index}.choices.${choiceIndex}.text`)}
                                className = "w-full p-4 outline-none font-mono font-bold text-lg bg-transparent placeholder:text-ink/40 uppercase"
                                placeholder = {`ANSWER ${choiceIndex + 1}`}
                            />
                        </div>
                    ))}
                </div>
            </div>
        </div>

    )

}